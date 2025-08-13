"""
LLM kullanarak fonksiyon analizi yapan modül
"""

import requests
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from ..utils.config import config
from ..utils.logger import get_logger
from dotenv import load_dotenv
import os

load_dotenv()

logger = get_logger(__name__)


@dataclass
class ParameterAnalysis:
    """Parametre analizi sonucu"""
    name: str
    type: str
    description: str
    constraints: List[str]
    valid_range: Optional[Dict[str, Any]] = None
    invalid_values: List[Any] = None
    boundary_values: List[Any] = None
    equivalence_classes: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.constraints is None:
            self.constraints = []
        if self.invalid_values is None:
            self.invalid_values = []
        if self.boundary_values is None:
            self.boundary_values = []
        if self.equivalence_classes is None:
            self.equivalence_classes = []


@dataclass
class FunctionAnalysis:
    """Fonksiyon analizi sonucu"""
    name: str
    description: str
    parameters: List[ParameterAnalysis]
    return_type: str
    return_constraints: List[str]
    preconditions: List[str]
    postconditions: List[str]
    error_conditions: List[str]
    test_scenarios: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.return_constraints is None:
            self.return_constraints = []
        if self.preconditions is None:
            self.preconditions = []
        if self.postconditions is None:
            self.postconditions = []
        if self.error_conditions is None:
            self.error_conditions = []
        if self.test_scenarios is None:
            self.test_scenarios = []


class LLMAnalyzer:
    """LLM kullanarak fonksiyon analizi yapan sınıf"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        
        # LLM API key zorunlu
        if not self.api_key:
            raise ValueError("LLM analizi için OpenRouter API key zorunludur!")
        
        self.logger.info("OpenRouter API client başarıyla oluşturuldu")
        
    def analyze_function(self, function_info) -> FunctionAnalysis:
        """
        Fonksiyonu LLM ile analiz et
        
        Args:
            function_info: DoxygenFunction objesi veya Dict[str, Any]
            
        Returns:
            FunctionAnalysis objesi
        """
        # DoxygenFunction objesini dict'e çevir
        if hasattr(function_info, 'name'):
            # DoxygenFunction objesi
            function_dict = {
                'name': function_info.name,
                'signature': function_info.signature,
                'brief': function_info.brief,
                'details': function_info.details,
                'params': [
                    {
                        'name': param.name,
                        'description': param.description,
                        'type': param.type,
                        'direction': param.direction
                    }
                    for param in function_info.params
                ],
                'return_info': {
                    'description': function_info.return_info.description if function_info.return_info else None,
                    'type': function_info.return_info.type if function_info.return_info else None
                } if function_info.return_info else None
            }
        else:
            # Zaten dict
            function_dict = function_info
        
        self.logger.info(f"Fonksiyon analiz ediliyor: {function_dict['name']}")
        
        # LLM'e gönderilecek prompt'u hazırla
        prompt = self._create_analysis_prompt(function_dict)
        
        try:
            # LLM'den analiz al
            response = self._get_llm_analysis(prompt)
            
            # Response'u FunctionAnalysis objesine çevir
            analysis = self._parse_llm_response(function_dict, response)
            
            self.logger.info(f"Fonksiyon analizi tamamlandı: {function_dict['name']}")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Fonksiyon analizi hatası: {e}")
            # Hata durumunda basit bir analiz döndür
            return self._create_default_analysis(function_dict)
    
    def _create_analysis_prompt(self, function_info: Dict[str, Any]) -> str:
        """
        LLM analizi için prompt oluştur
        
        Args:
            function_info: Fonksiyon bilgileri
            
        Returns:
            Analiz prompt'u
        """
        prompt = f"""
Senin görevin, verilen C fonksiyonlarına yönelik Ceedling test çerçeveleriyle uyumlu C birim test kodu üretmektir. Kurallara kesinlikle uymalısın:

ÖNEMLİ: Fonksiyon adı "{function_info['name']}" olarak kalmalı, hiç değiştirilmemeli!

1. Sadece geçerli, çalıştırılabilir ve derlenebilir C test kodu üret
2. Kod dışında yorum, açıklama veya başka içerik EKLEME
3. Tüm test fonksiyonlarını tek bir dosyada grupla
4. Test fonksiyonlarını şu formatta adlandır: test_<orijinal_fonksiyon_adı>__<senaryo>
5. Unity test makrolarını kullan: TEST_ASSERT_TRUE, TEST_ASSERT_FALSE, TEST_ASSERT_EQUAL_INT, TEST_ASSERT_EQUAL_STRING, TEST_ASSERT_NULL, TEST_ASSERT_NOT_NULL vb.
6. Fonksiyon enum parametresi alıyorsa, geçersiz değerler için açık cast kullan: (enum_t)(...)
7. Fonksiyonun dönüş değeri varsa mutlaka test et
8. Doxygen açıklamalarındaki parametre aralıklarını, sınır değerlerini ve eşdeğer sınıfları temel al
9. Fonksiyon void ise, global değişken, output parametresi gibi yan etkileri test et.

TEST KALİTESİ KURALLARI:
- Test edilen fonksiyon isimleri gerçek fonksiyonlarla tam uyumlu olmalı.
- Beklenen çıktılar fonksiyonların gerçek çıktılarıyla birebir eşleşmeli.
- String veya sabit değerlerde küçük farklılıklar olmamalı.
- Sınır değerler ve geçersiz girişler mutlaka test edilmeli.
- Gereksiz tekrarlar önlenmeli, odaklanmış test fonksiyonları kullanılmalı.
- Taşma, belirsiz veya tanımsız davranış gösteren durumlar test edilmemeli.
- Testler sade ve anlaşılır olmalı.

Aşağıdaki teknikleri kullanarak test fonksiyonlarını oluştur:

Equivalence Partitioning (EP):
- Her parametre için geçerli ve geçersiz eşdeğer sınıflar oluştur.
- Her sınıftan en az bir test vakası yaz
- Sınıflar arasında gereksiz tekrarlar olmamalı.

Boundary Value Analysis (BVA):
- Sayısal ve sıralı parametrelerde:
  * Minimum geçerli değer
  * Minimum geçersiz değer (bir önceki değer)
  * Maksimum geçerli değer
  * Maksimum geçersiz değer (bir sonraki değer)
- Enum parametrelerde enumun sınır değerleri kullanılarak test yapılmalı.
- Sınır değerler için ayrı test fonksiyonları oluştur.

Error Handling:
- Geçersiz girişler için hata durumları test edilmeli.
- NULL pointer durumları kontrol edilmeli.
- Taşma/underflow durumları sadece fonksiyon bunları handle ediyorsa test edilmeli.

Test Organizasyonu:
- Her test senaryosu için ayrı test fonksiyonu
- Benzer testler gruplandırılmalı
- Test fonksiyon isimleri açıklayıcı olmalı
- Gereksiz tekrarlar önlenmeli

Doxygen formatında tanımlanan parametre açıklamaları, test değerlerinin belirlenmesinde temel alınmalıdır. Parametre aralıkları belirtilmemişse, C veri tipinin sınırları (örn. INT_MIN, INT_MAX) kullanılarak analiz yapılmalıdır.
Yalnızca C dilinde, Ceedling ile uyumlu, test dosyası formatında sadece test fonksiyonu üret. Hiçbir yorum satırı ekleme ve kodlarda asla tekrara düşme.

ÖNEMLİ KURALLAR:
- Sadece C test kodunu döndür. JSON, açıklama veya başka hiçbir şey ekleme.
- Test edilen fonksiyonun adını ve parametrelerini ASLA değiştirme
- Test fonksiyon isimlerinde MUTLAKA orijinal fonksiyon adını kullan
- Fonksiyon adını çevirme, değiştirme veya farklı bir isimle yazma
- Orijinal fonksiyon adı: "{function_info['name']}" - Bu ismi aynen kullan
- Test fonksiyonlarında fonksiyon çağrısı yaparken: {function_info['name']}(parametreler) şeklinde yaz
- Fonksiyon imzasını: {function_info['signature']} şeklinde aynen koru

FONKSİYON BİLGİLERİ:
- İsim: {function_info['name']}
- İmza: {function_info['signature']}
- Açıklama: {function_info['brief']}
- Detaylar: {function_info.get('details', 'Yok')}

FONKSİYON KODU:
{function_info.get('code', 'Kod bulunamadı')}

PARAMETRELER (Doxygen formatındaki açıklamaları analiz et):
"""
        
        for param in function_info['params']:
            prompt += f"""
- {param['name']}: {param['description']}
  - Tip: {param.get('type', 'Belirtilmemiş')}
  - Yön: {param.get('direction', 'Belirtilmemiş')}
  
  Doxygen açıklamasını analiz et ve şunları çıkar:
  * Parametre aralığı (min, max değerler)
  * Geçerli değer sınıfları
  * Geçersiz değer sınıfları
  * Sınır değerleri
  * Özel kısıtlamalar
"""
        
        if function_info.get('return'):
            prompt += f"""
DÖNÜŞ DEĞERİ:
- Açıklama: {function_info['return']['description']}
- Tip: {function_info['return'].get('type', 'Belirtilmemiş')}
"""
        
        if function_info.get('preconditions'):
            prompt += f"""
ÖNKOŞULLAR:
"""
            for pre in function_info['preconditions']:
                prompt += f"- {pre}\n"
        
        if function_info.get('postconditions'):
            prompt += f"""
SONKOŞULLAR:
"""
            for post in function_info['postconditions']:
                prompt += f"- {post}\n"
        
        prompt += f"""

TEST KODU ÜRETME TALİMATLARI:
1. Fonksiyonun gerçek mantığını ve amacını anla.
2. Her parametre için Doxygen açıklamasını detaylı analiz et.
3. Parametre aralıklarını, kısıtlamalarını ve sınır değerlerini çıkar.
4. Equivalence Partitioning için geçerli ve geçersiz değer sınıflarını belirle.
5. Boundary Value Analysis için sınır değerlerini belirle.
6. Hata durumlarını ve özel durumları tespit et.
7. Her test senaryosu için beklenen sonucu hesapla (fonksiyon mantığına göre).
8. Sadece C test kodunu üret, başka hiçbir şey ekleme.

KALİTE KONTROL:
1. Test fonksiyon isimleri açıklayıcı ve anlamlı olmalı (Test fonksiyonları `test_<fonksiyon_adı>__<senaryo>` biçiminde olmalı.).
2. Beklenen çıktılar fonksiyonun gerçek davranışıyla tam uyumlu olmalı.
3. String değerler birebir eşleşmeli (büyük/küçük harf, boşluk, noktalama).
4. Sınır değerler doğru test edilmeli.
5. Üretilen test fonksiyonlarında gereksiz tekrarlar olmamalı.
6. Her test senaryosu için ayrı test fonksiyonu.
7. Testler sade ve anlaşılır olmalı.
8. Taşma/underflow gibi belirsiz durumlar test edilmemeli.

Analiz yaparken şunlara dikkat et:
1. Equivalence Partitioning (EP) için geçerli ve geçersiz değer sınıflarını belirle.
2. Boundary Value Analysis (BVA) için sınır değerlerini belirle.
3. Hata durumlarını ve özel durumları tespit et.
4. Her parametre için veri tipini ve kısıtlamaları çıkar.
5. Fonksiyonun davranışını ve beklenen sonuçları belirle.
6. Sadece C test kodunu döndür, JSON veya açıklama ekleme.

SON UYARI:
- Fonksiyon adı "{function_info['name']}" olarak kalmalı, değiştirilmemeli.
- Test fonksiyonlarında fonksiyon çağrısı: {function_info['name']}(parametreler) şeklinde olmalı.
- Fonksiyon imzası: {function_info['signature']} şeklinde korunmalı.
- Fonksiyon adını çevirme, Türkçe'ye çevirme veya farklı bir isimle yazma.
- Fonksiyon adını İngilizce'ye çevirme, aynen koru.
- Include dosyası: #include "{function_info['name']}.h" şeklinde olmalı.
- Fonksiyon adı "{function_info['name']}" - Bu ismi hiç değiştirme.
- Beklenen çıktıları fonksiyonun gerçek çıktılarıyla tam olarak eşleştir.
- String değerlerde büyük/küçük harf, boşluk ve noktalama işaretlerine dikkat et.
"""
        
        return prompt
    
    def _get_llm_analysis(self, prompt: str) -> str:
        """
        OpenRouter API'den analiz al
        
        Args:
            prompt: Analiz prompt'u
            
        Returns:
            LLM yanıtı
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/c-ai-test",
                "X-Title": "C-AI-Test"
            }
            
            data = {
                "model": "deepseek/deepseek-chat-v3-0324:free",
                "messages": [
                    {
                        "role": "system",
                        "content": "Sen bir C fonksiyon analiz uzmanısın. Black Box test teknikleri konusunda uzman olarak, fonksiyonları analiz edip test senaryoları üretirsin."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"OpenRouter API hatası: {e}")
            raise
        except Exception as e:
            self.logger.error(f"LLM API hatası: {e}")
            raise
    
    def _parse_llm_response(self, function_dict: Dict[str, Any], response: str) -> FunctionAnalysis:
        """
        LLM response'unu FunctionAnalysis objesine çevir
        
        Args:
            function_dict: Fonksiyon bilgileri
            response: LLM response'u
            
        Returns:
            FunctionAnalysis objesi
        """
        try:
            # LLM response'unda C test kodu varsa, onu kullan
            if response and len(response.strip()) > 0:
                # LLM'den gelen C test kodunu FunctionAnalysis'e ekle
                analysis = self._create_default_analysis(function_dict)
                analysis.test_scenarios = [{
                    'type': 'llm_generated',
                    'code': response,
                    'description': 'LLM tarafından üretilen C test kodu'
                }]
                return analysis
            else:
                # Boş response ise varsayılan analiz döndür
                return self._create_default_analysis(function_dict)
        except Exception as e:
            self.logger.error(f"LLM response parse hatası: {e}")
            return self._create_default_analysis(function_dict)
    
    def _create_default_analysis(self, function_dict: Dict[str, Any]) -> FunctionAnalysis:
        """
        Varsayılan analiz oluştur
        
        Args:
            function_dict: Fonksiyon bilgileri
            
        Returns:
            FunctionAnalysis objesi
        """
        # Parametreleri analiz et
        parameters = []
        for param in function_dict.get('params', []):
            param_analysis = ParameterAnalysis(
                name=param['name'],
                type=param.get('type', 'int') or 'int',  # None ise 'int' kullan
                description=param.get('description', ''),
                constraints=[],
                valid_range={'min': -1000, 'max': 1000},
                invalid_values=[None],
                boundary_values=[-1000, 0, 1000],
                equivalence_classes=[
                    {
                        'name': 'negative', 
                        'values': [-1000, -1],
                        'description': 'Negatif değerler',
                        'representative_value': -1,
                        'expected_behavior': 'valid'
                    },
                    {
                        'name': 'zero', 
                        'values': [0],
                        'description': 'Sıfır değeri',
                        'representative_value': 0,
                        'expected_behavior': 'valid'
                    },
                    {
                        'name': 'positive', 
                        'values': [1, 1000],
                        'description': 'Pozitif değerler',
                        'representative_value': 1,
                        'expected_behavior': 'valid'
                    }
                ]
            )
            parameters.append(param_analysis)
        
        # Return type'ı çıkar
        return_type = 'int'
        if function_dict.get('return_info'):
            return_type = function_dict['return_info'].get('type', 'int')
        
        return FunctionAnalysis(
            name=function_dict['name'],
            description=function_dict.get('brief', ''),
            parameters=parameters,
            return_type=return_type,
            return_constraints=[],
            preconditions=[],
            postconditions=[],
            error_conditions=['null_pointer', 'invalid_input']
        )
    
