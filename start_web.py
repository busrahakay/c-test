#!/usr/bin/env python3
"""
C Test Üreticisi - Web Arayüzü Başlatıcı

Bu script, web arayüzünü kolayca başlatmak için kullanılır.
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

def check_requirements():
    """Gereksinimleri kontrol et"""
    print("🔍 Gereksinimler kontrol ediliyor...")
    
    # Python versiyonu kontrolü
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ gerekli!")
        return False
    
    # Flask kontrolü
    try:
        import flask
        print("✅ Flask yüklü")
    except ImportError:
        print("❌ Flask yüklü değil. Yükleniyor...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "flask"])
    
    # Diğer bağımlılıkları kontrol et
    required_packages = [
        "requests", "openai", "python-dotenv", "loguru", "werkzeug"
    ]
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} yüklü")
        except ImportError:
            print(f"❌ {package} yüklü değil. Yükleniyor...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
    return True

def check_api_key():
    """API anahtarını kontrol et"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("⚠️  UYARI: OPENAI_API_KEY environment variable'ı ayarlanmamış!")
        print("   LLM analizi çalışmayacak.")
        print("   API anahtarınızı ayarlamak için:")
        print("   Windows: set OPENAI_API_KEY=your-api-key-here")
        print("   Linux/Mac: export OPENAI_API_KEY=your-api-key-here")
        return False
    else:
        print("✅ OpenAI API anahtarı ayarlanmış")
        return True

def create_directories():
    """Gerekli klasörleri oluştur"""
    directories = ['uploads', 'logs', 'templates']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ {directory}/ klasörü hazır")

def start_server():
    """Web sunucusunu başlat"""
    print("\n🚀 Web arayüzü başlatılıyor...")
    print("   URL: http://localhost:5000")
    print("   Durdurmak için Ctrl+C tuşlayın")
    print("-" * 50)
    
    try:
        # Tarayıcıyı aç
        time.sleep(2)
        webbrowser.open('http://localhost:5000')
        
        # Flask uygulamasını başlat - .env dosyasını yükleme
        env = os.environ.copy()
        env['FLASK_LOAD_DOTENV'] = 'false'
        subprocess.run([sys.executable, "app.py"], env=env)
        
    except KeyboardInterrupt:
        print("\n\n👋 Web arayüzü durduruldu.")
    except Exception as e:
        print(f"\n❌ Hata: {e}")

def main():
    """Ana fonksiyon"""
    print("=" * 60)
    print("🎯 C Test Üreticisi - Web Arayüzü Başlatıcı")
    print("=" * 60)
    
    # Gereksinimleri kontrol et
    if not check_requirements():
        print("\n❌ Gereksinimler karşılanamadı!")
        return
    
    # API anahtarını kontrol et
    check_api_key()
    
    # Klasörleri oluştur
    create_directories()
    
    # Sunucuyu başlat
    start_server()

if __name__ == "__main__":
    main() 