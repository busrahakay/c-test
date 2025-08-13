"""
Test runner modülü - Üretilen testleri çalıştıran araçlar
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class TestResult:
    """Test sonucu"""
    test_name: str
    status: str  # PASS, FAIL, ERROR
    output: str
    error: Optional[str] = None
    execution_time: Optional[float] = None


@dataclass
class TestSuiteResult:
    """Test suite sonucu"""
    suite_name: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    error_tests: int
    results: List[TestResult]
    execution_time: float


class TestRunner:
    """Test runner sınıfı"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def compile_test(self, test_file: Path, output_file: Optional[Path] = None) -> bool:
        """
        Test dosyasını derle
        
        Args:
            test_file: Test dosyası
            output_file: Çıkış dosyası
            
        Returns:
            Derleme başarı durumu
        """
        if output_file is None:
            output_file = test_file.parent / f"{test_file.stem}_test"
        
        self.logger.info(f"Test derleniyor: {test_file}")
        
        try:
            # GCC ile derle
            cmd = [
                'gcc',
                '-o', str(output_file),
                str(test_file),
                '-lm',  # math kütüphanesi için
                '-Wall',  # Tüm uyarıları göster
                '-Wextra'  # Ek uyarılar
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.logger.info(f"Test başarıyla derlendi: {output_file}")
                return True
            else:
                self.logger.error(f"Derleme hatası: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error("Derleme zaman aşımı")
            return False
        except Exception as e:
            self.logger.error(f"Derleme hatası: {e}")
            return False
    
    def run_test(self, test_executable: Path) -> TestSuiteResult:
        """
        Test executable'ını çalıştır
        
        Args:
            test_executable: Test executable dosyası
            
        Returns:
            Test sonuçları
        """
        self.logger.info(f"Test çalıştırılıyor: {test_executable}")
        
        try:
            import time
            start_time = time.time()
            
            result = subprocess.run(
                [str(test_executable)],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            execution_time = time.time() - start_time
            
            # Çıktıyı analiz et
            output = result.stdout
            error = result.stderr
            
            # Basit sonuç analizi
            if result.returncode == 0:
                status = "PASS"
                passed_tests = 1
                failed_tests = 0
                error_tests = 0
            else:
                status = "FAIL"
                passed_tests = 0
                failed_tests = 1
                error_tests = 0
            
            test_result = TestResult(
                test_name=test_executable.stem,
                status=status,
                output=output,
                error=error,
                execution_time=execution_time
            )
            
            suite_result = TestSuiteResult(
                suite_name=test_executable.stem,
                total_tests=1,
                passed_tests=passed_tests,
                failed_tests=failed_tests,
                error_tests=error_tests,
                results=[test_result],
                execution_time=execution_time
            )
            
            self.logger.info(f"Test tamamlandı: {status}")
            return suite_result
            
        except subprocess.TimeoutExpired:
            self.logger.error("Test zaman aşımı")
            
            test_result = TestResult(
                test_name=test_executable.stem,
                status="ERROR",
                output="",
                error="Test zaman aşımı",
                execution_time=60.0
            )
            
            return TestSuiteResult(
                suite_name=test_executable.stem,
                total_tests=1,
                passed_tests=0,
                failed_tests=0,
                error_tests=1,
                results=[test_result],
                execution_time=60.0
            )
            
        except Exception as e:
            self.logger.error(f"Test çalıştırma hatası: {e}")
            
            test_result = TestResult(
                test_name=test_executable.stem,
                status="ERROR",
                output="",
                error=str(e),
                execution_time=0.0
            )
            
            return TestSuiteResult(
                suite_name=test_executable.stem,
                total_tests=1,
                passed_tests=0,
                failed_tests=0,
                error_tests=1,
                results=[test_result],
                execution_time=0.0
            )
    
    def run_test_suite(self, test_file: Path) -> TestSuiteResult:
        """
        Test suite'ini çalıştır (derle + çalıştır)
        
        Args:
            test_file: Test dosyası
            
        Returns:
            Test sonuçları
        """
        self.logger.info(f"Test suite çalıştırılıyor: {test_file}")
        
        # Testi derle
        if not self.compile_test(test_file):
            return TestSuiteResult(
                suite_name=test_file.stem,
                total_tests=0,
                passed_tests=0,
                failed_tests=0,
                error_tests=1,
                results=[],
                execution_time=0.0
            )
        
        # Testi çalıştır
        executable = test_file.parent / f"{test_file.stem}_test"
        return self.run_test(executable)
    
    def generate_report(self, results: List[TestSuiteResult], output_file: Optional[Path] = None) -> str:
        """
        Test raporu oluştur
        
        Args:
            results: Test sonuçları
            output_file: Rapor dosyası
            
        Returns:
            Rapor içeriği
        """
        report = []
        report.append("=" * 60)
        report.append("BLACK BOX TEST RAPORU")
        report.append("=" * 60)
        report.append("")
        
        total_suites = len(results)
        total_tests = sum(r.total_tests for r in results)
        total_passed = sum(r.passed_tests for r in results)
        total_failed = sum(r.failed_tests for r in results)
        total_errors = sum(r.error_tests for r in results)
        
        # Özet
        report.append("ÖZET:")
        report.append(f"  Toplam Test Suite: {total_suites}")
        report.append(f"  Toplam Test: {total_tests}")
        report.append(f"  Başarılı: {total_passed}")
        report.append(f"  Başarısız: {total_failed}")
        report.append(f"  Hata: {total_errors}")
        report.append("")
        
        # Detaylı sonuçlar
        for suite_result in results:
            report.append(f"Test Suite: {suite_result.suite_name}")
            report.append("-" * 40)
            report.append(f"  Toplam Test: {suite_result.total_tests}")
            report.append(f"  Başarılı: {suite_result.passed_tests}")
            report.append(f"  Başarısız: {suite_result.failed_tests}")
            report.append(f"  Hata: {suite_result.error_tests}")
            report.append(f"  Çalışma Süresi: {suite_result.execution_time:.2f} saniye")
            report.append("")
            
            for test_result in suite_result.results:
                report.append(f"  Test: {test_result.test_name}")
                report.append(f"    Durum: {test_result.status}")
                if test_result.error:
                    report.append(f"    Hata: {test_result.error}")
                if test_result.execution_time:
                    report.append(f"    Süre: {test_result.execution_time:.2f} saniye")
                report.append("")
        
        report_content = "\n".join(report)
        
        # Dosyaya yaz
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            self.logger.info(f"Rapor oluşturuldu: {output_file}")
        
        return report_content 