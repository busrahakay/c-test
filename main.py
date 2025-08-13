#!/usr/bin/env python3
"""
C Fonksiyonları için Otomatik Black Box Test Üreticisi

Bu program, C dilinde yazılmış fonksiyonlar için otomatik olarak
Black Box test fonksiyonları üretir.
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Optional

# Proje modüllerini import et
sys.path.append(str(Path(__file__).parent / "src"))

from src.parser.doxygen_parser import DoxygenParser, DoxygenFunction
from src.analyzer.llm_analyzer import LLMAnalyzer, FunctionAnalysis
from src.generator.test_generator import TestGenerator, GeneratedTestSuite
from src.utils.config import config
from src.utils.logger import get_logger, setup_logger

logger = get_logger(__name__)


class BlackBoxTestGenerator:
    """Ana Black Box test üretici sınıfı"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.doxygen_parser = DoxygenParser()
        self.llm_analyzer = LLMAnalyzer()
        self.test_generator = TestGenerator()
    
    def generate_tests_from_examples(self, examples_dir: Path = None, tests_dir: Path = None) -> bool:
        """
        Examples klasöründeki tüm C dosyaları için tests klasörüne test dosyaları oluştur
        
        Args:
            examples_dir: Examples klasörü yolu (varsayılan: ./examples)
            tests_dir: Tests klasörü yolu (varsayılan: ./tests)
            
        Returns:
            Başarı durumu
        """
        if examples_dir is None:
            examples_dir = Path("examples")
        
        if tests_dir is None:
            tests_dir = Path("tests")
        
        # Tests klasörünü oluştur (yoksa)
        tests_dir.mkdir(exist_ok=True)
        
        if not examples_dir.exists():
            self.logger.error(f"Examples klasörü bulunamadı: {examples_dir}")
            return False
        
        # Examples klasöründeki tüm .c dosyalarını bul
        c_files = list(examples_dir.glob("*.c"))
        
        if not c_files:
            self.logger.warning(f"Examples klasöründe C dosyası bulunamadı: {examples_dir}")
            return False
        
        self.logger.info(f"{len(c_files)} C dosyası bulundu: {examples_dir}")
        
        success_count = 0
        
        for c_file in c_files:
            try:
                self.logger.info(f"İşleniyor: {c_file.name}")
                
                # Test dosyası adını oluştur
                test_file = tests_dir / f"{c_file.stem}_tests.c"
                
                # Test üret
                success = self.generate_tests_from_file(c_file, test_file)
                
                if success:
                    success_count += 1
                    self.logger.info(f"Test dosyası oluşturuldu: {test_file}")
                else:
                    self.logger.error(f"Test üretimi başarısız: {c_file.name}")
                    
            except Exception as e:
                self.logger.error(f"Dosya işlenirken hata: {c_file.name} - {e}")
        
        self.logger.info(f"Toplam {success_count}/{len(c_files)} dosya başarıyla işlendi")
        return success_count > 0
    
    def generate_tests_from_file(self, input_file: Path, output_file: Optional[Path] = None) -> bool:
        """
        Dosyadan test üret
        
        Args:
            input_file: Giriş C dosyası
            output_file: Çıkış test dosyası
            
        Returns:
            Başarı durumu
        """
        try:
            self.logger.info(f"Test üretimi başlatılıyor: {input_file}")
            
            # 1. Doxygen fonksiyonlarını parse et
            functions = self.doxygen_parser.parse_file(input_file)
            
            if not functions:
                self.logger.error("Doxygen fonksiyonu bulunamadı")
                return False
            
            self.logger.info(f"{len(functions)} fonksiyon bulundu")
            
            # 2. Her fonksiyon için test üret
            all_test_suites = []
            
            for function in functions:
                self.logger.info(f"Fonksiyon analiz ediliyor: {function.name}")
                
                # Fonksiyon bilgilerini al
                function_info = self.doxygen_parser.get_function_info(function)
                
                # LLM ile analiz et
                llm_response = self.llm_analyzer.analyze_function(function_info)
                
                # Test suite'i üret
                test_suite = self.test_generator.generate_tests(llm_response)
                all_test_suites.append((test_suite, llm_response))
            
            # 3. C kodu üret
            if output_file is None:
                output_file = input_file.parent / f"{input_file.stem}_tests.c"
            
            self._write_test_file(all_test_suites, output_file)
            
            self.logger.info(f"Test dosyası oluşturuldu: {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Test üretimi başarısız: {e}")
            return False
    
    def generate_tests_from_content(self, content: str, function_name: str = "test_function") -> str:
        """
        İçerikten test üret
        
        Args:
            content: C dosyası içeriği
            function_name: Fonksiyon adı
            
        Returns:
            Üretilen C test kodu
        """
        try:
            self.logger.info("İçerikten test üretimi başlatılıyor")
            
            # 1. Doxygen fonksiyonlarını parse et
            functions = self.doxygen_parser.parse_content(content)
            
            if not functions:
                self.logger.error("Doxygen fonksiyonu bulunamadı")
                return ""
            
            # 2. İlk fonksiyonu al
            function = functions[0]
            function_info = self.doxygen_parser.get_function_info(function)
            
            # 3. LLM ile analiz et
            llm_response = self.llm_analyzer.analyze_function(function_info)
            
            # 4. Test suite'i üret
            test_suite = self.test_generator.generate_tests(llm_response)
            
            # 5. C kodu üret
            c_code = self.test_generator.generate_c_code(test_suite, llm_response)
            
            self.logger.info("Test kodu üretildi")
            return c_code
            
        except Exception as e:
            self.logger.error(f"Test üretimi başarısız: {e}")
            return ""
    
    def _write_test_file(self, test_suites: List[tuple], output_file: Path) -> None:
        """
        Test dosyasını yaz
        
        Args:
            test_suites: (test_suite, llm_response) tuple'ları listesi
            output_file: Çıkış dosyası
        """
        # Çıkış dizinini oluştur
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Tüm test suite'lerini birleştir
        combined_code = self._combine_test_suites(test_suites)
        
        # Dosyaya yaz
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(combined_code)
    
    def _combine_test_suites(self, test_suites: List[tuple]) -> str:
        """
        Test suite'lerini birleştir
        
        Args:
            test_suites: (test_suite, llm_response) tuple'ları listesi
            
        Returns:
            Birleştirilmiş C kodu
        """
        if len(test_suites) == 1:
            test_suite, llm_response = test_suites[0]
            return self.test_generator.generate_c_code(test_suite, llm_response)
        
        # Birden fazla test suite varsa birleştir
        combined_code = """// Otomatik üretilmiş Black Box test suite'i
// Birden fazla fonksiyon için testler

"""
        
        # Ortak include'lar
        combined_code += """#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

"""
        
        # Her test suite için ayrı test fonksiyonları
        for test_suite, llm_response in test_suites:
            c_code = self.test_generator.generate_c_code(test_suite, llm_response)
            
            # Main fonksiyonunu çıkar
            lines = c_code.split('\n')
            main_start = -1
            main_end = -1
            
            for i, line in enumerate(lines):
                if 'int main(' in line:
                    main_start = i
                elif main_start != -1 and line.strip() == '}':
                    main_end = i + 1
                    break
            
            if main_start != -1 and main_end != -1:
                # Main fonksiyonunu çıkar
                test_code = '\n'.join(lines[:main_start])
            else:
                test_code = c_code
            
            combined_code += test_code + "\n\n"
        
        # Birleştirilmiş main fonksiyonu
        combined_code += """int main(void) {
    printf("Black Box Test Suite Başlatılıyor\\n\\n");
    
"""
        
        for test_suite, llm_response in test_suites:
            for test_func in test_suite.test_functions:
                combined_code += f"    {test_func.name}();\n"
        
        combined_code += """    
    printf("Tüm testler tamamlandı\\n");
    return 0;
}
"""
        
        return combined_code


def main():
    """Ana program fonksiyonu"""
    parser = argparse.ArgumentParser(
        description="C Fonksiyonları için Otomatik Black Box Test Üreticisi",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  python main.py --examples                    # Examples klasöründeki tüm dosyalar için test üret
  python main.py --input function.c --output tests.c
  python main.py --input src/math.c --framework unity
  python main.py --input examples/calculator.c --config config.yaml
        """
    )
    
    parser.add_argument(
        '--examples', '-e',
        action='store_true',
        help='Examples klasöründeki tüm C dosyaları için tests klasörüne test dosyaları oluştur'
    )
    
    parser.add_argument(
        '--input', '-i',
        type=Path,
        help='Giriş C dosyası (Doxygen formatında)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=Path,
        help='Çıkış test dosyası (varsayılan: input_tests.c)'
    )
    
    parser.add_argument(
        '--framework', '-f',
        choices=['unity', 'cmocka', 'custom'],
        default='custom',
        help='Test framework (varsayılan: custom)'
    )
    
    parser.add_argument(
        '--config', '-c',
        type=Path,
        help='Konfigürasyon dosyası'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Log seviyesi (varsayılan: INFO)'
    )
    
    parser.add_argument(
        '--log-file',
        type=Path,
        help='Log dosyası'
    )
    
    args = parser.parse_args()
    
    # Log seviyesini ayarla
    setup_logger(
        log_file=args.log_file,
        level=args.log_level
    )
    
    # Konfigürasyonu güncelle
    if args.framework:
        config.test.framework = args.framework
    
    # Konfigürasyon dosyasını yükle (eğer belirtilmişse)
    if args.config and args.config.exists():
        # TODO: Konfigürasyon dosyası yükleme
        pass
    
    # Konfigürasyonu doğrula
    try:
        config.validate()
    except ValueError as e:
        logger.error(f"Konfigürasyon hatası: {e}")
        sys.exit(1)
    
    # Test üreticiyi başlat
    generator = BlackBoxTestGenerator()
    
    # Examples klasöründeki tüm dosyalar için test üret
    if args.examples:
        logger.info("Examples klasöründeki tüm C dosyaları için test üretimi başlatılıyor...")
        success = generator.generate_tests_from_examples()
        
        if success:
            logger.info("Examples klasörü işlemi başarıyla tamamlandı")
            sys.exit(0)
        else:
            logger.error("Examples klasörü işlemi başarısız")
            sys.exit(1)
    
    # Tek dosya için test üret
    if args.input:
        # Giriş dosyasını kontrol et
        if not args.input.exists():
            logger.error(f"Giriş dosyası bulunamadı: {args.input}")
            sys.exit(1)
        
        # Test üret
        success = generator.generate_tests_from_file(args.input, args.output)
        
        if success:
            logger.info("Test üretimi başarıyla tamamlandı")
            sys.exit(0)
        else:
            logger.error("Test üretimi başarısız")
            sys.exit(1)
    
    # Hiçbir argüman verilmemişse yardım göster
    if not args.examples and not args.input:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main() 