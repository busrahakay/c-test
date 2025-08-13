"""
Ana test generator modülü
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass

from ..analyzer.llm_analyzer import FunctionAnalysis
from ..utils.config import config
from ..utils.logger import get_logger
from .ep_generator import EPGenerator, EPTestScenario
from .bva_generator import BVAGenerator, BVATestScenario

logger = get_logger(__name__)


@dataclass
class TestFunction:
    """Test fonksiyonu"""
    name: str
    description: str
    test_cases: List[Dict[str, Any]]
    setup_code: str = ""
    teardown_code: str = ""


@dataclass
class GeneratedTestSuite:
    """Üretilen test suite'i"""
    function_name: str
    test_functions: List[TestFunction]
    includes: List[str]
    setup_code: str
    teardown_code: str
    test_code: str = ""
    ep_tests: List = None
    bva_tests: List = None
    
    def __post_init__(self):
        if self.ep_tests is None:
            self.ep_tests = []
        if self.bva_tests is None:
            self.bva_tests = []


class TestGenerator:
    """Ana test generator sınıfı"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.ep_generator = EPGenerator()
        self.bva_generator = BVAGenerator()
        
        # Test framework şablonları
        self.framework_templates = {
            'unity': self._unity_template,
            'cmocka': self._cmocka_template,
            'custom': self._custom_template
        }
    
    def generate_tests(self, llm_response: str) -> GeneratedTestSuite:
        """
        LLM yanıtından test suite'i üret
        
        Args:
            llm_response: LLM'den gelen C test kodu
            
        Returns:
            Üretilen test suite'i
        """
        self.logger.info("LLM yanıtından test suite üretiliyor")
        
        # LLM'den gelen C test kodunu direkt kullan
        # Basit bir test suite oluştur
        test_function = TestFunction(
            name="test_from_llm",
            description="LLM tarafından üretilen test fonksiyonu",
            test_cases=[],
            setup_code="",
            teardown_code=""
        )
        
        # Test suite'i oluştur
        test_suite = GeneratedTestSuite(
            function_name="llm_generated_function",
            test_functions=[test_function],
            includes=["unity.h"],
            setup_code="",
            teardown_code=""
        )
        
        self.logger.info("LLM yanıtından test suite üretildi")
        return test_suite
    
    def generate_from_content(self, content: str, framework: str = 'custom', 
                            include_ep: bool = True, include_bva: bool = True) -> GeneratedTestSuite:
        """
        C içeriğinden test suite üret
        
        Args:
            content: C kodu içeriği
            framework: Test framework'ü ('unity', 'cmocka', 'custom')
            include_ep: EP testlerini dahil et
            include_bva: BVA testlerini dahil et
            
        Returns:
            Üretilen test suite
        """
        self.logger.info(f"C içeriğinden test suite üretiliyor (framework: {framework})")
        
        # Doxygen parser ile fonksiyonları parse et
        from ..parser.doxygen_parser import DoxygenParser
        parser = DoxygenParser()
        functions = parser.parse_content(content)
        
        if not functions:
            self.logger.warning("Doxygen formatında fonksiyon bulunamadı")
            # Basit bir test suite döndür
            return GeneratedTestSuite(
                function_name="unknown_function",
                test_functions=[],
                includes=[],
                setup_code="",
                teardown_code=""
            )
        
        # İlk fonksiyonu al
        function = functions[0]
        
        # LLM analyzer ile analiz et
        from ..analyzer.llm_analyzer import LLMAnalyzer
        analyzer = LLMAnalyzer()
        
        try:
            analysis = analyzer.analyze_function(function)
            
            # EP testleri üret
            ep_tests = []
            if include_ep:
                ep_tests = self.ep_generator.generate_ep_tests(analysis.parameters)
            
            # BVA testleri üret
            bva_tests = []
            if include_bva:
                bva_tests = self.bva_generator.generate_bva_tests(analysis.parameters)
            
            # Test fonksiyonlarını oluştur
            test_functions = self._create_test_functions(analysis, ep_tests, bva_tests)
            
            # Test suite oluştur
            test_suite = GeneratedTestSuite(
                function_name=function.name,
                test_functions=test_functions,
                includes=self._get_includes(analysis),
                setup_code=self._get_setup_code(analysis),
                teardown_code=self._get_teardown_code(analysis),
                ep_tests=ep_tests,
                bva_tests=bva_tests
            )
            
            # LLM'den gelen test kodu varsa onu kullan, yoksa generate_c_code ile üret
            llm_test_code = None
            if analysis.test_scenarios:
                for scenario in analysis.test_scenarios:
                    if scenario.get('type') == 'llm_generated' and scenario.get('code'):
                        llm_test_code = scenario['code']
                        break
            
            test_suite.test_code = self.generate_c_code(test_suite, framework=framework, llm_response=llm_test_code)
            
            self.logger.info(f"Test suite başarıyla üretildi: {len(test_functions)} test fonksiyonu")
            return test_suite
            
        except Exception as e:
            self.logger.error(f"Test suite üretimi hatası: {e}")
            # Hata durumunda basit bir test suite döndür
            return GeneratedTestSuite(
                function_name=function.name,
                test_functions=[],
                includes=[],
                setup_code="",
                teardown_code=""
            )
    
    def generate_c_code(self, test_suite: GeneratedTestSuite, llm_response: str = None, framework: str = 'custom') -> str:
        """
        Test suite'i C kodu olarak üret
        
        Args:
            test_suite: Test suite'i
            llm_response: LLM'den gelen C test kodu (opsiyonel)
            framework: Test framework'ü ('unity', 'cmocka', 'custom')
            
        Returns:
            C kodu
        """
        self.logger.info(f"C test kodu üretiliyor (framework: {framework})")
        
        # Eğer LLM yanıtı varsa, onu direkt kullan
        if llm_response:
            return llm_response
        
        # Framework template'ini al
        template_func = self.framework_templates.get(framework, self._custom_template)
        
        # C kodu üret
        c_code = template_func(test_suite)
        
        self.logger.info("C test kodu üretildi")
        return c_code
    
    def _create_test_functions(self, analysis: FunctionAnalysis, 
                              ep_tests: List[EPTestScenario], 
                              bva_tests: List[BVATestScenario]) -> List[TestFunction]:
        """
        Test fonksiyonlarını oluştur
        
        Args:
            analysis: Fonksiyon analizi
            ep_tests: EP test senaryoları
            bva_tests: BVA test senaryoları
            
        Returns:
            Test fonksiyonları listesi
        """
        test_functions = []
        
        # EP test fonksiyonu - sadece anlamlı testler varsa
        if ep_tests and len(ep_tests) > 0:
            ep_function = TestFunction(
                name=f"test_{analysis.name}_equivalence_partitioning",
                description="Equivalence Partitioning testleri",
                test_cases=[self._scenario_to_test_case(test) for test in ep_tests[:5]]  # Maksimum 5 test
            )
            test_functions.append(ep_function)
        
        # BVA test fonksiyonu - sadece anlamlı testler varsa
        if bva_tests and len(bva_tests) > 0:
            bva_function = TestFunction(
                name=f"test_{analysis.name}_boundary_value_analysis",
                description="Boundary Value Analysis testleri",
                test_cases=[self._scenario_to_test_case(test) for test in bva_tests[:5]]  # Maksimum 5 test
            )
            test_functions.append(bva_function)
        
        # Hata durumu test fonksiyonu - sadece gerçek hata durumları varsa
        if analysis.error_conditions and len(analysis.error_conditions) > 0:
            # Sadece anlamlı hata durumları için test oluştur
            meaningful_errors = [error for error in analysis.error_conditions 
                               if any(keyword in error.lower() for keyword in 
                                     ['null', 'invalid', 'negative', 'zero', 'overflow', 'underflow'])]
            
            if meaningful_errors:
                error_function = TestFunction(
                    name=f"test_{analysis.name}_error_conditions",
                    description="Hata durumu testleri",
                    test_cases=self._create_error_test_cases(analysis, meaningful_errors)
                )
                test_functions.append(error_function)
        
        return test_functions
    
    def _scenario_to_test_case(self, scenario) -> Dict[str, Any]:
        """
        Test senaryosunu test case'e çevir
        
        Args:
            scenario: Test senaryosu
            
        Returns:
            Test case
        """
        return {
            'name': scenario.name,
            'description': scenario.description,
            'input_values': scenario.input_values,
            'expected_output': scenario.expected_output,
            'test_type': getattr(scenario, 'test_type', 'unknown')
        }
    
    def _create_error_test_cases(self, analysis: FunctionAnalysis, meaningful_errors: List[str]) -> List[Dict[str, Any]]:
        """
        Anlamlı hata durumu test case'leri oluştur
        
        Args:
            analysis: Fonksiyon analizi
            meaningful_errors: Anlamlı hata durumları listesi
            
        Returns:
            Hata test case'leri
        """
        test_cases = []
        
        for i, error_condition in enumerate(meaningful_errors):
            # Hata durumu için uygun input değerleri oluştur
            input_values = {}
            for param in analysis.parameters:
                if "null" in error_condition.lower() and param.type.lower() in ['string', 'char*', 'void*']:
                    input_values[param.name] = None
                elif "negative" in error_condition.lower() and param.type.lower() in ['int', 'float', 'double']:
                    input_values[param.name] = -1
                elif "zero" in error_condition.lower() and param.type.lower() in ['int', 'float', 'double']:
                    input_values[param.name] = 0
                elif "overflow" in error_condition.lower() and param.type.lower() in ['int', 'short', 'long']:
                    input_values[param.name] = 2147483647  # INT_MAX
                elif "underflow" in error_condition.lower() and param.type.lower() in ['int', 'short', 'long']:
                    input_values[param.name] = -2147483648  # INT_MIN
                else:
                    input_values[param.name] = self._get_default_value(param)
            
            test_case = {
                'name': f"error_case_{i}",
                'description': f"Hata durumu: {error_condition}",
                'input_values': input_values,
                'expected_output': 'error',
                'test_type': 'error'
            }
            test_cases.append(test_case)
        
        return test_cases
    
    def _get_default_value(self, param) -> Any:
        """
        Parametre için varsayılan değer al
        
        Args:
            param: Parametre analizi
            
        Returns:
            Varsayılan değer
        """
        param_type = param.type.lower()
        
        if param_type in ['int', 'short', 'long']:
            return 0
        elif param_type in ['float', 'double']:
            return 0.0
        elif param_type in ['char*', 'string']:
            return ""
        elif param_type == 'bool':
            return False
        elif param_type == 'char':
            return 'a'
        else:
            return None
    
    def _get_includes(self, analysis: FunctionAnalysis) -> List[str]:
        """
        Gerekli include'ları al
        
        Args:
            analysis: Fonksiyon analizi
            
        Returns:
            Include listesi
        """
        includes = [
            "#include <stdio.h>",
            "#include <stdlib.h>",
            "#include <string.h>",
            "#include <assert.h>"
        ]
        
        # Test framework include'ları
        if config.test.framework == 'unity':
            includes.append("#include \"unity.h\"")
        elif config.test.framework == 'cmocka':
            includes.append("#include <cmocka.h>")
        
        # Fonksiyon header'ı - dosya adından türet
        function_file = analysis.name
        includes.append(f"#include \"{function_file}.h\"")
        
        return includes
    
    def _get_setup_code(self, analysis: FunctionAnalysis) -> str:
        """
        Setup kodu al
        
        Args:
            analysis: Fonksiyon analizi
            
        Returns:
            Setup kodu
        """
        setup_code = f"""
void setUp(void) {{
    // Test setup kodu
    // Burada gerekli başlangıç işlemleri yapılabilir
}}
"""
        return setup_code
    
    def _get_teardown_code(self, analysis: FunctionAnalysis) -> str:
        """
        Teardown kodu al
        
        Args:
            analysis: Fonksiyon analizi
            
        Returns:
            Teardown kodu
        """
        teardown_code = f"""
void tearDown(void) {{
    // Test cleanup kodu
    // Burada gerekli temizlik işlemleri yapılabilir
}}
"""
        return teardown_code
    
    def _unity_template(self, test_suite: GeneratedTestSuite) -> str:
        """
        Unity framework template'i
        
        Args:
            test_suite: Test suite'i
            
        Returns:
            Unity C kodu
        """
        code = f"""// {test_suite.function_name} için Unity test suite'i
// Otomatik olarak üretilmiştir

"""
        
        # Include'lar
        for include in test_suite.includes:
            code += f"{include}\n"
        
        code += "\n"
        
        # Setup ve teardown
        code += test_suite.setup_code + "\n"
        code += test_suite.teardown_code + "\n"
        
        # Test fonksiyonları
        for test_func in test_suite.test_functions:
            code += f"void {test_func.name}(void) {{\n"
            
            for i, test_case in enumerate(test_func.test_cases):
                # Test case başlığı
                code += f"    // Test Case {i+1}: {test_case['description']}\n"
                
                # Input değerlerini hazırla
                param_vars = []
                for param_name, param_value in test_case['input_values'].items():
                    if param_value is None:
                        code += f"    // {param_name} = NULL (pointer parametresi)\n"
                        param_vars.append("NULL")
                    elif isinstance(param_value, str) and param_value.startswith('"') and param_value.endswith('"'):
                        # String değeri
                        code += f"    const char* {param_name} = {param_value};\n"
                        param_vars.append(param_name)
                    elif isinstance(param_value, str) and param_value in ['"-2147483648"', '"2147483647"']:
                        # C sabitleri
                        const_value = param_value.strip('"')
                        code += f"    int {param_name} = {const_value};\n"
                        param_vars.append(param_name)
                    elif isinstance(param_value, str) and param_value.isdigit():
                        # Sayısal string
                        code += f"    int {param_name} = {param_value};\n"
                        param_vars.append(param_name)
                    elif isinstance(param_value, str) and param_value.startswith('-') and param_value[1:].isdigit():
                        # Negatif sayısal string
                        code += f"    int {param_name} = {param_value};\n"
                        param_vars.append(param_name)
                    elif isinstance(param_value, (int, float)):
                        # Sayısal değer
                        code += f"    int {param_name} = {param_value};\n"
                        param_vars.append(param_name)
                    else:
                        # Diğer değerler
                        code += f"    int {param_name} = {param_value};\n"
                        param_vars.append(param_name)
                
                # Beklenen sonuç - C sözdizimi kurallarına uygun
                expected_output = test_case['expected_output']
                if isinstance(expected_output, str) and expected_output.isdigit():
                    code += f"    int expected_result = {expected_output};\n"
                elif isinstance(expected_output, str) and expected_output.startswith('-') and expected_output[1:].isdigit():
                    code += f"    int expected_result = {expected_output};\n"
                elif isinstance(expected_output, str) and expected_output in ['"-2147483648"', '"2147483647"']:
                    const_value = expected_output.strip('"')
                    code += f"    int expected_result = {const_value};\n"
                elif isinstance(expected_output, (int, float)):
                    code += f"    int expected_result = {expected_output};\n"
                elif expected_output == 'error':
                    code += f"    // Bu test case hata durumu simüle eder\n"
                    code += f"    // expected_result tanımlanmaz çünkü hata beklenir\n"
                else:
                    # Güvenli varsayılan değer
                    code += f"    int expected_result = 0;\n"
                
                # Fonksiyon çağrısı - sadece hata durumu değilse
                if expected_output != 'error':
                    param_list = ", ".join(param_vars)
                    code += f"    int actual_result = {test_suite.function_name}({param_list});\n"
                    
                    # Unity assert kontrolü
                    code += f"    TEST_ASSERT_EQUAL_INT(expected_result, actual_result);\n"
                else:
                    code += f"    // Hata durumu testi - fonksiyon çağrısı yapılmaz\n"
                    code += f"    // TEST_ASSERT_EQUAL_INT(expected_result, actual_result);\n"
                
                code += "\n"
            
            code += "}\n\n"
        
        # Main fonksiyonu
        code += f"""int main(void) {{
    UNITY_BEGIN();
"""
        
        for test_func in test_suite.test_functions:
            code += f"    RUN_TEST({test_func.name});\n"
        
        code += """    return UNITY_END();
}
"""
        
        return code
    
    def _cmocka_template(self, test_suite: GeneratedTestSuite) -> str:
        """
        CMocka framework template'i
        
        Args:
            test_suite: Test suite'i
            
        Returns:
            CMocka C kodu
        """
        code = f"""// {test_suite.function_name} için CMocka test suite'i
// Otomatik olarak üretilmiştir

"""
        
        # Include'lar
        for include in test_suite.includes:
            code += f"{include}\n"
        
        code += "\n"
        
        # Test fonksiyonları
        for test_func in test_suite.test_functions:
            code += f"static void {test_func.name}(void **state) {{\n"
            
            for i, test_case in enumerate(test_func.test_cases):
                # Test case başlığı
                code += f"    // Test Case {i+1}: {test_case['description']}\n"
                
                # Input değerlerini hazırla
                param_vars = []
                for param_name, param_value in test_case['input_values'].items():
                    if param_value is None:
                        code += f"    // {param_name} = NULL (pointer parametresi)\n"
                        param_vars.append("NULL")
                    elif isinstance(param_value, str) and param_value.startswith('"') and param_value.endswith('"'):
                        # String değeri
                        code += f"    const char* {param_name} = {param_value};\n"
                        param_vars.append(param_name)
                    elif isinstance(param_value, str) and param_value in ['"-2147483648"', '"2147483647"']:
                        # C sabitleri
                        const_value = param_value.strip('"')
                        code += f"    int {param_name} = {const_value};\n"
                        param_vars.append(param_name)
                    elif isinstance(param_value, str) and param_value.isdigit():
                        # Sayısal string
                        code += f"    int {param_name} = {param_value};\n"
                        param_vars.append(param_name)
                    elif isinstance(param_value, str) and param_value.startswith('-') and param_value[1:].isdigit():
                        # Negatif sayısal string
                        code += f"    int {param_name} = {param_value};\n"
                        param_vars.append(param_name)
                    elif isinstance(param_value, (int, float)):
                        # Sayısal değer
                        code += f"    int {param_name} = {param_value};\n"
                        param_vars.append(param_name)
                    else:
                        # Diğer değerler
                        code += f"    int {param_name} = {param_value};\n"
                        param_vars.append(param_name)
                
                # Beklenen sonuç - C sözdizimi kurallarına uygun
                expected_output = test_case['expected_output']
                if isinstance(expected_output, str) and expected_output.isdigit():
                    code += f"    int expected_result = {expected_output};\n"
                elif isinstance(expected_output, str) and expected_output.startswith('-') and expected_output[1:].isdigit():
                    code += f"    int expected_result = {expected_output};\n"
                elif isinstance(expected_output, str) and expected_output in ['"-2147483648"', '"2147483647"']:
                    const_value = expected_output.strip('"')
                    code += f"    int expected_result = {const_value};\n"
                elif isinstance(expected_output, (int, float)):
                    code += f"    int expected_result = {expected_output};\n"
                elif expected_output == 'error':
                    code += f"    // Bu test case hata durumu simüle eder\n"
                    code += f"    // expected_result tanımlanmaz çünkü hata beklenir\n"
                else:
                    # Güvenli varsayılan değer
                    code += f"    int expected_result = 0;\n"
                
                # Fonksiyon çağrısı - sadece hata durumu değilse
                if expected_output != 'error':
                    param_list = ", ".join(param_vars)
                    code += f"    int actual_result = {test_suite.function_name}({param_list});\n"
                    
                    # CMocka assert kontrolü
                    code += f"    assert_int_equal(expected_result, actual_result);\n"
                else:
                    code += f"    // Hata durumu testi - fonksiyon çağrısı yapılmaz\n"
                    code += f"    // assert_int_equal(expected_result, actual_result);\n"
                
                code += "\n"
            
            code += "}\n\n"
        
        # Test array'i
        code += "int main(void) {\n"
        code += "    const struct CMUnitTest tests[] = {\n"
        
        for test_func in test_suite.test_functions:
            code += f"        cmocka_unit_test({test_func.name}),\n"
        
        code += "    };\n"
        code += "    return cmocka_run_group_tests(tests, NULL, NULL);\n"
        code += "}\n"
        
        return code
    
    def _custom_template(self, test_suite: GeneratedTestSuite) -> str:
        """
        Özel test framework template'i
        
        Args:
            test_suite: Test suite'i
            
        Returns:
            Özel C kodu
        """
        code = f"""// {test_suite.function_name} için özel test suite'i
// Otomatik olarak üretilmiştir

"""
        
        # Include'lar
        for include in test_suite.includes:
            code += f"{include}\n"
        
        code += "\n"
        
        # Test fonksiyonları
        for test_func in test_suite.test_functions:
            code += f"void {test_func.name}(void) {{\n"
            code += f"    printf(\"Running {test_func.description}\\n\");\n\n"
            
            for i, test_case in enumerate(test_func.test_cases):
                # Test case başlığı
                code += f"    // Test Case {i+1}: {test_case['description']}\n"
                
                # Input değerlerini hazırla
                param_vars = []
                for param_name, param_value in test_case['input_values'].items():
                    if param_value is None:
                        code += f"    // {param_name} = NULL (pointer parametresi)\n"
                        param_vars.append("NULL")
                    elif isinstance(param_value, str) and param_value.startswith('"') and param_value.endswith('"'):
                        # String değeri
                        code += f"    const char* {param_name} = {param_value};\n"
                        param_vars.append(param_name)
                    elif isinstance(param_value, str) and param_value in ['"-2147483648"', '"2147483647"']:
                        # C sabitleri
                        const_value = param_value.strip('"')
                        code += f"    int {param_name} = {const_value};\n"
                        param_vars.append(param_name)
                    elif isinstance(param_value, str) and param_value.isdigit():
                        # Sayısal string
                        code += f"    int {param_name} = {param_value};\n"
                        param_vars.append(param_name)
                    elif isinstance(param_value, str) and param_value.startswith('-') and param_value[1:].isdigit():
                        # Negatif sayısal string
                        code += f"    int {param_name} = {param_value};\n"
                        param_vars.append(param_name)
                    elif isinstance(param_value, (int, float)):
                        # Sayısal değer
                        code += f"    int {param_name} = {param_value};\n"
                        param_vars.append(param_name)
                    else:
                        # Diğer değerler
                        code += f"    int {param_name} = {param_value};\n"
                        param_vars.append(param_name)
                
                # Beklenen sonuç - C sözdizimi kurallarına uygun
                expected_output = test_case['expected_output']
                if isinstance(expected_output, str) and expected_output.isdigit():
                    code += f"    int expected_result = {expected_output};\n"
                elif isinstance(expected_output, str) and expected_output.startswith('-') and expected_output[1:].isdigit():
                    code += f"    int expected_result = {expected_output};\n"
                elif isinstance(expected_output, str) and expected_output in ['"-2147483648"', '"2147483647"']:
                    const_value = expected_output.strip('"')
                    code += f"    int expected_result = {const_value};\n"
                elif isinstance(expected_output, (int, float)):
                    code += f"    int expected_result = {expected_output};\n"
                elif expected_output == 'error':
                    code += f"    // Bu test case hata durumu simüle eder\n"
                    code += f"    // expected_result tanımlanmaz çünkü hata beklenir\n"
                else:
                    # Güvenli varsayılan değer
                    code += f"    int expected_result = 0;\n"
                
                # Fonksiyon çağrısı - sadece hata durumu değilse
                if expected_output != 'error':
                    param_list = ", ".join(param_vars)
                    code += f"    int actual_result = {test_suite.function_name}({param_list});\n"
                    
                    # Custom assert kontrolü
                    code += f"    if (expected_result != actual_result) {{\n"
                    code += f"        printf(\"FAILED: Test Case {i+1}\\n\");\n"
                    code += f"        printf(\"  Expected: %d\\n\", expected_result);\n"
                    code += f"        printf(\"  Actual: %d\\n\", actual_result);\n"
                    code += f"        printf(\"  Input: {param_list}\\n\");\n"
                    code += f"        assert(0); // Test failed\n"
                    code += f"    }} else {{\n"
                    code += f"        printf(\"PASSED: Test Case {i+1}\\n\");\n"
                    code += f"    }}\n"
                else:
                    code += f"    // Hata durumu testi - fonksiyon çağrısı yapılmaz\n"
                    code += f"    printf(\"SKIPPED: Test Case {i+1} (hata durumu simülasyonu)\\n\");\n"
                
                code += "\n"
            
            code += "    printf(\"Test completed\\n\\n\");\n"
            code += "}\n\n"
        
        # Main fonksiyonu
        code += f"""int main(void) {{
    printf("Starting {test_suite.function_name} tests\\n\\n");
"""
        
        for test_func in test_suite.test_functions:
            code += f"    {test_func.name}();\n"
        
        code += """    printf("All tests completed\\n");
    return 0;
}
"""
        
        return code 
    
    def _calculate_expected_result(self, test_case: Dict[str, Any], function_name: str) -> Any:
        """
        Test case için beklenen sonucu hesapla
        
        Args:
            test_case: Test case
            function_name: Fonksiyon adı
            
        Returns:
            Beklenen sonuç
        """
        expected_output = test_case['expected_output']
        input_values = test_case['input_values']
        
        # Eğer expected_output zaten hesaplanmışsa onu kullan
        if expected_output != 'error' and expected_output != 0:
            return expected_output
        
        # Fonksiyon mantığına göre hesapla
        if function_name == 'find_max':
            # find_max fonksiyonu için mantık
            values = []
            for value in input_values.values():
                if isinstance(value, (int, float)):
                    values.append(value)
                elif isinstance(value, str) and value.isdigit():
                    values.append(int(value))
                elif isinstance(value, str) and value.startswith('-') and value[1:].isdigit():
                    values.append(int(value))
                elif isinstance(value, str) and value in ['"-2147483648"', '"2147483647"']:
                    const_value = value.strip('"')
                    values.append(int(const_value))
            
            if values:
                return max(values)
        
        # Diğer fonksiyonlar için varsayılan
        return expected_output