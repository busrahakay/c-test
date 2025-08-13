#!/usr/bin/env python3
"""
C Fonksiyonları için Otomatik Black Box Test Üreticisi - Web Arayüzü

Bu Flask uygulaması, C fonksiyonları için otomatik test üretimi sağlar.
"""

import os
import sys
import json
import tempfile
from pathlib import Path
from typing import List, Dict, Any
from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
import zipfile
import io
from dotenv import load_dotenv

load_dotenv()

# Proje modüllerini import et
sys.path.append(str(Path(__file__).parent / "src"))

from src.parser.doxygen_parser import DoxygenParser, DoxygenFunction
from src.analyzer.llm_analyzer import LLMAnalyzer, FunctionAnalysis
from src.generator.test_generator import TestGenerator, GeneratedTestSuite
from src.utils.config import config
from src.utils.logger import get_logger, setup_logger

# Flask uygulamasını oluştur
app = Flask(__name__)
app.secret_key = 'c-ai-test-secret-key-2024'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Logger'ı ayarla
setup_logger()
logger = get_logger(__name__)

# Upload klasörünü oluştur
UPLOAD_FOLDER = Path('uploads')
UPLOAD_FOLDER.mkdir(exist_ok=True)
app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)

# İzin verilen dosya uzantıları
ALLOWED_EXTENSIONS = {'c', 'h'}

def allowed_file(filename):
    """Dosya uzantısının izin verilen uzantılardan olup olmadığını kontrol et"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class WebTestGenerator:
    """Web arayüzü için test üretici sınıfı"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.doxygen_parser = DoxygenParser()
        self.llm_analyzer = LLMAnalyzer()
        self.test_generator = TestGenerator()
    
    def analyze_file_content(self, content: str) -> Dict[str, Any]:
        """Dosya içeriğini analiz et ve fonksiyonları çıkar"""
        try:
            # Doxygen parser ile fonksiyonları parse et
            functions = self.doxygen_parser.parse_content(content)
            
            if not functions:
                return {
                    'success': False,
                    'error': 'Dosyada Doxygen formatında fonksiyon bulunamadı'
                }
            
            # Her fonksiyon için LLM analizi yap
            analyzed_functions = []
            for func in functions:
                try:
                    analysis = self.llm_analyzer.analyze_function(func)
                    analyzed_functions.append({
                        'name': func.name,
                        'signature': func.signature,
                        'brief': func.brief,
                        'details': func.details,
                        'params': [
                            {
                                'name': param.name,
                                'description': param.description,
                                'type': param.type,
                                'direction': param.direction
                            }
                            for param in func.params
                        ],
                        'return_info': {
                            'description': func.return_info.description if func.return_info else None,
                            'type': func.return_info.type if func.return_info else None
                        } if func.return_info else None,
                        'analysis': analysis
                    })
                except Exception as e:
                    self.logger.error(f"Fonksiyon analizi hatası: {func.name} - {e}")
                    analyzed_functions.append({
                        'name': func.name,
                        'signature': func.signature,
                        'brief': func.brief,
                        'details': func.details,
                        'params': [
                            {
                                'name': param.name,
                                'description': param.description,
                                'type': param.type,
                                'direction': param.direction
                            }
                            for param in func.params
                        ],
                        'return_info': {
                            'description': func.return_info.description if func.return_info else None,
                            'type': func.return_info.type if func.return_info else None
                        } if func.return_info else None,
                        'analysis': None,
                        'error': str(e)
                    })
            
            return {
                'success': True,
                'functions': analyzed_functions,
                'total_functions': len(functions)
            }
            
        except Exception as e:
            self.logger.error(f"Dosya analizi hatası: {e}")
            return {
                'success': False,
                'error': f'Dosya analizi hatası: {str(e)}'
            }
    
    def generate_tests(self, content: str, framework: str = 'custom', 
                      include_ep: bool = True, include_bva: bool = True) -> Dict[str, Any]:
        """Test dosyaları üret"""
        try:
            # Test üret
            test_suite = self.test_generator.generate_from_content(
                content=content,
                framework=framework,
                include_ep=include_ep,
                include_bva=include_bva
            )
            
            return {
                'success': True,
                'test_code': test_suite.test_code,
                'framework': framework,
                'ep_tests': test_suite.ep_tests,
                'bva_tests': test_suite.bva_tests
            }
            
        except Exception as e:
            self.logger.error(f"Test üretimi hatası: {e}")
            return {
                'success': False,
                'error': f'Test üretimi hatası: {str(e)}'
            }

# Global test generator instance
test_generator = WebTestGenerator()

@app.route('/')
def index():
    """Ana sayfa"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_file():
    """Dosya analizi endpoint'i"""
    try:
        # JSON verisi veya dosya yükleme kontrol et
        if request.is_json:
            # JSON verisi olarak gönderilmiş
            data = request.get_json()
            content = data.get('content', '')
            if not content:
                return jsonify({'success': False, 'error': 'İçerik boş'})
        else:
            # Dosya yükleme olarak gönderilmiş
            if 'file' not in request.files:
                return jsonify({'success': False, 'error': 'Dosya yüklenmedi'})
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'success': False, 'error': 'Dosya seçilmedi'})
            
            if not allowed_file(file.filename):
                return jsonify({'success': False, 'error': 'Geçersiz dosya türü. Sadece .c ve .h dosyaları kabul edilir.'})
            
            # Dosya içeriğini oku
            content = file.read().decode('utf-8')
        
        # Dosyayı analiz et
        result = test_generator.analyze_file_content(content)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Dosya analizi hatası: {e}")
        return jsonify({'success': False, 'error': f'Beklenmeyen hata: {str(e)}'})

@app.route('/generate', methods=['POST'])
def generate_tests():
    """Test üretimi endpoint'i"""
    try:
        logger.info("Generate endpoint çağrıldı")
        data = request.get_json()
        
        logger.info(f"Request data: {data}")
        
        if not data or 'content' not in data:
            logger.error("İçerik bulunamadı")
            return jsonify({'success': False, 'error': 'İçerik bulunamadı'})
        
        content = data['content']
        framework = data.get('framework', 'custom')
        include_ep = data.get('include_ep', True)
        include_bva = data.get('include_bva', True)
        
        logger.info(f"Framework: {framework}, EP: {include_ep}, BVA: {include_bva}")
        logger.info(f"Content length: {len(content)}")
        
        # Test üret
        result = test_generator.generate_tests(
            content=content,
            framework=framework,
            include_ep=include_ep,
            include_bva=include_bva
        )
        
        logger.info(f"Test üretimi sonucu: {result}")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Test üretimi hatası: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': f'Beklenmeyen hata: {str(e)}'})

@app.route('/download', methods=['POST'])
def download_tests():
    """Test dosyalarını indir"""
    try:
        data = request.get_json()
        
        if not data or 'test_code' not in data:
            return jsonify({'success': False, 'error': 'Test kodu bulunamadı'})
        
        test_code = data['test_code']
        filename = data.get('filename', 'generated_tests.c')
        
        # ZIP dosyası oluştur
        memory_file = io.BytesIO()
        
        with zipfile.ZipFile(memory_file, 'w') as zf:
            # Test dosyasını ekle
            zf.writestr(filename, test_code)
            
            # README dosyası ekle
            readme_content = f"""# Otomatik Üretilen Test Dosyaları

Bu dosyalar C Fonksiyonları için Otomatik Black Box Test Üreticisi tarafından oluşturulmuştur.

## Dosya İçeriği
- {filename}: Üretilen test fonksiyonları

## Kullanım
1. Test dosyasını projenize ekleyin
2. Gerekli test framework'ünü yükleyin
3. Testleri derleyin ve çalıştırın

## Test Framework'leri
- Unity: Basit ve hafif test framework
- CMocka: Mocking desteği olan test framework
- Custom: Özel test framework

## Not
Bu testler Equivalence Partitioning (EP) ve Boundary Value Analysis (BVA) teknikleri kullanılarak üretilmiştir.
"""
            zf.writestr('README.md', readme_content)
        
        memory_file.seek(0)
        
        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name='generated_tests.zip'
        )
        
    except Exception as e:
        logger.error(f"İndirme hatası: {e}")
        return jsonify({'success': False, 'error': f'İndirme hatası: {str(e)}'})

@app.route('/examples')
def examples():
    """Örnek dosyalar sayfası"""
    examples_dir = Path('examples')
    example_files = []
    
    if examples_dir.exists():
        for file in examples_dir.glob('*.c'):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                example_files.append({
                    'name': file.name,
                    'content': content,
                    'size': len(content)
                })
            except Exception as e:
                logger.error(f"Örnek dosya okuma hatası: {file} - {e}")
    
    return render_template('examples.html', examples=example_files)

@app.route('/api/examples')
def api_examples():
    """Örnek dosyalar API endpoint'i"""
    examples_dir = Path('examples')
    example_files = []
    
    if examples_dir.exists():
        for file in examples_dir.glob('*.c'):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                example_files.append({
                    'name': file.name,
                    'content': content,
                    'size': len(content)
                })
            except Exception as e:
                logger.error(f"Örnek dosya okuma hatası: {file} - {e}")
    
    return jsonify({'success': True, 'examples': example_files})

@app.errorhandler(413)
def too_large(e):
    """Dosya boyutu çok büyük hatası"""
    return jsonify({'success': False, 'error': 'Dosya boyutu çok büyük. Maksimum 16MB.'}), 413

@app.errorhandler(500)
def internal_error(e):
    """İç sunucu hatası"""
    logger.error(f"İç sunucu hatası: {e}")
    return jsonify({'success': False, 'error': 'İç sunucu hatası oluştu'}), 500

if __name__ == '__main__':
    # API anahtarını kontrol et
    if not os.getenv('OPENAI_API_KEY'):
        print("UYARI: OPENAI_API_KEY environment variable'ı ayarlanmamış!")
        print("LLM analizi çalışmayacak. Lütfen API anahtarınızı ayarlayın.")
    
    # Flask uygulamasını çalıştır - .env dosyasını otomatik yükleme
    app.run(debug=True, host='0.0.0.0', port=5000, load_dotenv=False) 