# C Test Üreticisi - Web Arayüzü

Bu dokümantasyon, C Fonksiyonları için Otomatik Black Box Test Üreticisi'nin web arayüzünü açıklar.

## Özellikler

### 🎨 Modern ve Kullanıcı Dostu Arayüz
- **Responsive Design**: Tüm cihazlarda mükemmel görünüm
- **Drag & Drop**: Dosyaları sürükleyip bırakarak yükleme
- **Syntax Highlighting**: C kodu için renkli kod gösterimi
- **Real-time Feedback**: Anlık geri bildirim ve durum güncellemeleri

### 📁 Dosya Yönetimi
- **Dosya Yükleme**: .c ve .h dosyalarını yükleme
- **Kod Editörü**: Doğrudan kod yazma ve düzenleme
- **Örnek Dosyalar**: Hazır örneklerle test etme
- **ZIP İndirme**: Üretilen testleri ZIP formatında indirme

### 🔧 Test Üretimi
- **Framework Seçimi**: Unity, CMocka, Custom framework desteği
- **Test Türleri**: EP (Equivalence Partitioning) ve BVA (Boundary Value Analysis)
- **LLM Analizi**: OpenAI GPT ile akıllı fonksiyon analizi
- **Anlık Sonuçlar**: Test üretim sürecini takip etme

## Kurulum

### 1. Gereksinimler
```bash
# Python 3.7+ gerekli
python --version

# Bağımlılıkları yükle
pip install -r requirements.txt
```

### 2. API Anahtarı Ayarlama
```bash
# Windows
set OPENAI_API_KEY=your-api-key-here

# Linux/Mac
export OPENAI_API_KEY=your-api-key-here
```

### 3. Uygulamayı Çalıştırma
```bash
# Web arayüzünü başlat
python app.py

# Tarayıcıda aç
# http://localhost:5000
```

## Kullanım

### Ana Sayfa
1. **Dosya Yükleme**: C dosyanızı sürükleyip bırakın veya "Dosya Seç" butonuna tıklayın
2. **Kod Editörü**: Alternatif olarak kodunuzu doğrudan editöre yazabilirsiniz
3. **Framework Seçimi**: Test framework'ünü seçin (Unity, CMocka, Custom)
4. **Test Türleri**: EP ve/veya BVA testlerini seçin
5. **Analiz**: "Dosyayı Analiz Et" butonuna tıklayın
6. **Test Üretimi**: "Test Üret" butonuna tıklayın
7. **İndirme**: Üretilen testleri indirin veya kopyalayın

### Örnekler Sayfası
- Mevcut örnek C dosyalarını görüntüleyin
- Örnekleri ana sayfaya yükleyin
- Doxygen formatı hakkında bilgi alın

## Doxygen Format Gereksinimleri

Web arayüzü, C fonksiyonlarınızın Doxygen formatında dokümante edilmiş olmasını gerektirir:

```c
/**
 * @brief Fonksiyon açıklaması
 * @param param1 İlk parametre açıklaması
 * @param param2 İkinci parametre açıklaması
 * @return Dönüş değeri açıklaması
 * @pre Önkoşullar (opsiyonel)
 * @post Sonkoşullar (opsiyonel)
 */
int function_name(int param1, char* param2) {
    // Fonksiyon implementasyonu
    return 0;
}
```

## API Endpoints

### POST /analyze
Dosya analizi için kullanılır.

**Request:**
- Content-Type: multipart/form-data
- file: C dosyası (.c veya .h)

**Response:**
```json
{
    "success": true,
    "functions": [
        {
            "name": "function_name",
            "signature": "int function_name(int param)",
            "description": "Fonksiyon açıklaması",
            "parameters": [...],
            "return_type": "int",
            "analysis": {...}
        }
    ],
    "total_functions": 1
}
```

### POST /generate
Test üretimi için kullanılır.

**Request:**
```json
{
    "content": "C kodu",
    "framework": "unity",
    "include_ep": true,
    "include_bva": true
}
```

**Response:**
```json
{
    "success": true,
    "test_code": "Üretilen test kodu",
    "framework": "unity",
    "ep_tests": [...],
    "bva_tests": [...]
}
```

### POST /download
Test dosyalarını ZIP formatında indirmek için kullanılır.

**Request:**
```json
{
    "test_code": "Test kodu",
    "filename": "generated_tests.c"
}
```

**Response:**
- Content-Type: application/zip
- Dosya: generated_tests.zip

### GET /examples
Örnek dosyaları listelemek için kullanılır.

**Response:**
```json
{
    "success": true,
    "examples": [
        {
            "name": "example.c",
            "content": "C kodu",
            "size": 1234
        }
    ]
}
```

## Dosya Yapısı

```
c-ai-test/
├── app.py                 # Flask web uygulaması
├── templates/             # HTML template'leri
│   ├── base.html         # Ana template
│   ├── index.html        # Ana sayfa
│   └── examples.html     # Örnekler sayfası
├── uploads/              # Yüklenen dosyalar (otomatik oluşturulur)
├── examples/             # Örnek C dosyaları
├── tests/               # Üretilen test dosyaları
└── src/                 # Ana uygulama modülleri
```

## Güvenlik

- **Dosya Boyutu Limiti**: Maksimum 16MB
- **Dosya Türü Kontrolü**: Sadece .c ve .h dosyaları
- **CSRF Koruması**: Flask-WTF ile CSRF koruması (gelecek sürümde)
- **Input Validation**: Tüm kullanıcı girdileri doğrulanır

## Hata Yönetimi

Web arayüzü aşağıdaki hata durumlarını yönetir:

- **Dosya Yükleme Hataları**: Geçersiz dosya türü, boyut aşımı
- **API Hataları**: OpenAI API bağlantı sorunları
- **Analiz Hataları**: Doxygen format hataları
- **Test Üretimi Hataları**: LLM analizi başarısızlıkları

## Geliştirme

### Yerel Geliştirme
```bash
# Geliştirme modunda çalıştır
export FLASK_ENV=development
python app.py
```

### Debug Modu
```bash
# Debug modunda çalıştır
python app.py --debug
```

### Logging
Uygulama, `loguru` kütüphanesi kullanarak kapsamlı loglama yapar:
- Dosya yükleme işlemleri
- API çağrıları
- Hata durumları
- Test üretim süreçleri

## Gelecek Özellikler

- [ ] **Kullanıcı Kimlik Doğrulama**: Kullanıcı hesapları ve oturum yönetimi
- [ ] **Proje Yönetimi**: Test projelerini kaydetme ve yönetme
- [ ] **Test Çalıştırma**: Web arayüzünden testleri çalıştırma
- [ ] **Coverage Analizi**: Test coverage raporları
- [ ] **Batch Processing**: Toplu dosya işleme
- [ ] **API Dokümantasyonu**: Swagger/OpenAPI entegrasyonu
- [ ] **Dark Mode**: Karanlık tema desteği
- [ ] **Çoklu Dil Desteği**: İngilizce ve diğer diller

## Sorun Giderme

### Yaygın Sorunlar

1. **API Anahtarı Hatası**
   ```
   UYARI: OPENAI_API_KEY environment variable'ı ayarlanmamış!
   ```
   **Çözüm**: API anahtarınızı environment variable olarak ayarlayın.

2. **Dosya Yükleme Hatası**
   ```
   Geçersiz dosya türü. Sadece .c ve .h dosyaları kabul edilir.
   ```
   **Çözüm**: Sadece .c ve .h uzantılı dosyalar yükleyin.

3. **Doxygen Format Hatası**
   ```
   Dosyada Doxygen formatında fonksiyon bulunamadı
   ```
   **Çözüm**: C fonksiyonlarınızı Doxygen formatında dokümante edin.

### Log Dosyaları
Hata ayıklama için log dosyalarını kontrol edin:
```bash
# Log dosyalarını görüntüle
tail -f logs/app.log
```

## Destek

Sorunlarınız için:
1. GitHub Issues sayfasını kontrol edin
2. Yeni issue oluşturun
3. Detaylı hata mesajları ve log dosyalarını ekleyin

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. 