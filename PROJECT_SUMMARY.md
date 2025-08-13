# C Fonksiyonları için Otomatik Black Box Test Üreticisi - Proje Özeti

## Proje Amaçları

Bu proje, C dilinde yazılmış fonksiyonlar için otomatik olarak Black Box test fonksiyonları üreten bir sistemdir. Sistem, özellikle **Equivalence Partitioning (EP)** ve **Boundary Value Analysis (BVA)** tekniklerini kullanarak test senaryoları oluşturur.

### Temel Özellikler

1. **Doxygen Parser**: C fonksiyonlarının Doxygen formatındaki dokümantasyonunu analiz eder
2. **LLM Analyzer**: **Zorunlu** - Fonksiyon analizi ve parametre aralığı çıkarma için LLM kullanır
3. **Equivalence Partitioning (EP)**: LLM analizine dayalı eşdeğerlik bölümleme tekniği ile test değerleri üretir
4. **Boundary Value Analysis (BVA)**: LLM analizine dayalı sınır değer analizi ile test değerleri üretir
5. **Test Generator**: Otomatik olarak C unit test fonksiyonları üretir
6. **Test Runner**: Üretilen testleri çalıştırır ve sonuçları raporlar
7. **Batch Processing**: Examples klasöründeki tüm C dosyaları için toplu test üretimi

## Sistem Mimarisi

### Ana Bileşenler

1. **Doxygen Parser** (`src/parser/doxygen_parser.py`)
   - C fonksiyonlarının Doxygen formatındaki dokümantasyonunu parse eder
   - Fonksiyon imzalarını, parametreleri, dönüş değerlerini ve açıklamalarını çıkarır
   - Multi-line Doxygen yorumlarını destekler

2. **LLM Analyzer** (`src/analyzer/llm_analyzer.py`)
   - **Zorunlu** - OpenAI GPT modellerini kullanarak fonksiyon analizi yapar
   - Doxygen açıklamalarından parametre aralıklarını çıkarır
   - Equivalence classes ve boundary values belirler
   - JSON formatında yapılandırılmış analiz sonucu döndürür

3. **EP Generator** (`src/generator/ep_generator.py`)
   - LLM analizine dayalı Equivalence Partitioning test senaryoları üretir
   - Geçerli ve geçersiz değer sınıflarını kullanır
   - Kombinasyon testleri oluşturur

4. **BVA Generator** (`src/generator/bva_generator.py`)
   - LLM analizine dayalı Boundary Value Analysis test senaryoları üretir
   - Sınır değerlerini ve yakın değerleri test eder
   - Veri tipine özgü sınır değerleri kullanır

5. **Test Generator** (`src/generator/test_generator.py`)
   - EP ve BVA testlerini birleştirir
   - Unity, CMocka ve custom test framework'leri destekler
   - C test kodu üretir

6. **Test Runner** (`src/runner/test_runner.py`)
   - Üretilen C test dosyalarını derler ve çalıştırır
   - Test sonuçlarını raporlar
   - GCC compiler kullanır

### Yardımcı Modüller

- **Config** (`src/utils/config.py`): Proje konfigürasyonu ve LLM ayarları
- **Logger** (`src/utils/logger.py`): Yapılandırılmış loglama sistemi

## Kullanım Senaryoları

### 1. Examples Klasöründeki Tüm Dosyalar İçin Test Üretimi

```bash
# Examples klasöründeki tüm C dosyaları için tests klasörüne test dosyaları oluştur
python main.py --examples
```

### 2. Tek Dosya İçin Test Üretimi

```bash
# Tek dosya için test üret
python main.py --input function.c --output tests.c

# Framework seçimi ile
python main.py --input examples/calculator.c --framework unity
```

## Proje Yapısı

```
c-ai-test/
├── examples/           # C fonksiyon dosyaları (Doxygen formatında)
│   ├── sample_functions.c
│   ├── string_utils.c
│   └── array_utils.c
├── tests/             # Üretilen test dosyaları
├── src/
│   ├── parser/        # Doxygen parser
│   │   ├── __init__.py
│   │   └── doxygen_parser.py
│   ├── analyzer/      # LLM analyzer (zorunlu)
│   │   ├── __init__.py
│   │   └── llm_analyzer.py
│   ├── generator/     # EP ve BVA generators
│   │   ├── __init__.py
│   │   ├── test_generator.py
│   │   ├── ep_generator.py
│   │   └── bva_generator.py
│   ├── runner/        # Test runner
│   │   ├── __init__.py
│   │   └── test_runner.py
│   └── utils/         # Config ve logger
│       ├── __init__.py
│       ├── config.py
│       └── logger.py
├── main.py            # Ana program
├── requirements.txt   # Bağımlılıklar
├── README.md          # Proje dokümantasyonu
└── PROJECT_SUMMARY.md # Bu dosya
```

## Teknik Detaylar

### LLM Analizi Zorunluluğu

Sistem, LLM analizini zorunlu kılar:
- `OPENAI_API_KEY` environment variable'ı gereklidir
- LLM olmadan test üretimi mümkün değildir
- Doxygen açıklamaları LLM tarafından analiz edilir
- Parametre aralıkları LLM analizine dayalı olarak belirlenir

### Desteklenen Test Framework'leri

1. **Unity**: Basit ve hafif test framework
2. **CMocka**: Mocking desteği olan test framework
3. **Custom**: Özel test framework (varsayılan)

### Doxygen Format Desteği

Sistem aşağıdaki Doxygen formatlarını destekler:
- `@brief`: Fonksiyon kısa açıklaması
- `@param`: Parametre açıklamaları
- `@return`: Dönüş değeri açıklaması
- `@pre`: Önkoşullar
- `@post`: Sonkoşullar

## Gereksinimler

### Zorunlu Gereksinimler
- Python 3.7+
- OpenAI API anahtarı (`OPENAI_API_KEY`)
- GCC compiler (test çalıştırma için)

### Python Bağımlılıkları
```
requests>=2.31.0
openai>=1.0.0
python-dotenv>=1.0.0
loguru>=0.7.0
```

## Kurulum ve Çalıştırma

### 1. Bağımlılıkları Yükle
```bash
pip install -r requirements.txt
```

### 2. API Anahtarını Ayarla
```bash
export OPENAI_API_KEY="your-api-key-here"
```

### 3. Examples Klasörüne C Dosyaları Ekle
C fonksiyonlarınızı Doxygen formatında `examples/` klasörüne koyun.

### 4. Test Üret
```bash
python main.py --examples
```

## Örnek Kullanım

### Giriş C Dosyası (examples/sample_functions.c)
```c
/**
 * @brief Yaş değeri geçerli mi kontrol eder.
 *
 * Geçerli yaşlar 0 ile 130 arasındadır.
 *
 * @param age Kontrol edilecek yaş.
 * @return true Geçerli yaş.
 * @return false Geçersiz yaş.
 */
bool is_valid_age(int age) {
    return (age >= 0 && age <= 130);
}
```

### Çıkış Test Dosyası (tests/sample_functions_tests.c)
```c
// LLM analizi ile üretilen EP ve BVA testleri
// - Yaş 0-130 arası geçerli
// - Yaş < 0 geçersiz
// - Yaş > 130 geçersiz
// - Sınır değerleri: -1, 0, 130, 131
```

## Gelecek Geliştirmeler

1. **Daha Fazla Test Framework Desteği**: Google Test, CUnit vb.
2. **Gelişmiş LLM Analizi**: Daha detaylı parametre analizi
3. **Test Coverage Analizi**: Üretilen testlerin coverage raporu
4. **CI/CD Entegrasyonu**: GitHub Actions, GitLab CI vb.
5. **Web Arayüzü**: Kullanıcı dostu web arayüzü
6. **Test Veritabanı**: Test sonuçlarının saklanması ve analizi

## Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## İletişim

Proje hakkında sorularınız için issue açabilirsiniz. 