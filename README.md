# C Fonksiyonları için Otomatik Black Box Test Üreticisi

Bu proje, C dilinde yazılmış fonksiyonlar için otomatik olarak Black Box test fonksiyonları üreten bir sistemdir. **LLM analizi zorunludur** ve Doxygen formatındaki parametre aralıklarını analiz ederek test fonksiyonları üretir.

## Özellikler

- **Doxygen Parser**: C fonksiyonlarının Doxygen formatındaki dokümantasyonunu analiz eder
- **LLM Integration**: **Zorunlu** - Fonksiyon analizi ve parametre aralığı çıkarma için LLM kullanır
- **Equivalence Partitioning (EP)**: LLM analizine dayalı eşdeğerlik bölümleme tekniği ile test değerleri üretir
- **Boundary Value Analysis (BVA)**: LLM analizine dayalı sınır değer analizi ile test değerleri üretir
- **Test Generator**: Otomatik olarak C unit test fonksiyonları üretir
- **Test Runner**: Üretilen testleri çalıştırır ve sonuçları raporlar
- **Batch Processing**: Examples klasöründeki tüm C dosyaları için toplu test üretimi

## Kurulum

```bash
pip install -r requirements.txt
```

## Gereksinimler

**Zorunlu**: OpenRouter API anahtarı sistemde yapılandırılmıştır.

## Kullanım

### Examples Klasöründeki Tüm Dosyalar İçin Test Üretimi

```bash
# Examples klasöründeki tüm C dosyaları için tests klasörüne test dosyaları oluştur
python main.py --examples
```

### Tek Dosya İçin Test Üretimi

```bash
# Tek dosya için test üret
python main.py --input function.c --output tests.c

# Framework seçimi ile
python main.py --input examples/calculator.c --framework unity
```

### Komut Satırı Seçenekleri

```bash
python main.py --help
```

**Seçenekler:**
- `--examples, -e`: Examples klasöründeki tüm C dosyaları için tests klasörüne test dosyaları oluştur
- `--input, -i`: Giriş C dosyası (Doxygen formatında)
- `--output, -o`: Çıkış test dosyası (varsayılan: input_tests.c)
- `--framework, -f`: Test framework (unity, cmocka, custom)
- `--log-level`: Log seviyesi (DEBUG, INFO, WARNING, ERROR)

## Proje Yapısı

```
c-ai-test/
├── examples/           # C fonksiyon dosyaları (Doxygen formatında)
├── tests/             # Üretilen test dosyaları
├── src/
│   ├── parser/        # Doxygen parser
│   ├── analyzer/      # LLM analyzer (zorunlu)
│   ├── generator/     # EP ve BVA generators
│   ├── runner/        # Test runner
│   └── utils/         # Config ve logger
├── main.py            # Ana program
└── requirements.txt   # Bağımlılıklar
```

## Çalışma Mantığı

1. **Examples Klasörü**: C fonksiyonlarınızı Doxygen formatında bu klasöre koyun
2. **Test Üretimi**: `python main.py --examples` komutu ile tüm dosyalar için test üretin
3. **Tests Klasörü**: Üretilen test dosyaları bu klasöre kaydedilir

**Not**: Sistem OpenRouter API'sini kullanarak DeepSeek modeli ile LLM analizi yapar. 