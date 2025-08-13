"""
Boundary Value Analysis (BVA) test değerleri üreten modül
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import random

from ..analyzer.llm_analyzer import ParameterAnalysis
from ..utils.logger import get_logger

logger = get_logger(__name__)

# C sabitleri
INT_MIN = -2147483648
INT_MAX = 2147483647
FLOAT_MIN = -3.402823e+38
FLOAT_MAX = 3.402823e+38


@dataclass
class BVATestValue:
    """BVA test değeri"""
    value: Any
    description: str
    boundary_type: str
    expected_behavior: str
    is_valid: bool


@dataclass
class BVATestScenario:
    """BVA test senaryosu"""
    name: str
    description: str
    input_values: Dict[str, Any]
    expected_output: Any
    boundary_values: Dict[str, str]
    test_type: str = "BVA"


class BVAGenerator:
    """Boundary Value Analysis test değerleri üreten sınıf"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        
        # Veri tipi bazlı boundary değerleri
        self.boundary_values = {
            'int': {
                'min': INT_MIN,
                'max': INT_MAX,
                'min_plus_one': INT_MIN + 1,
                'max_minus_one': INT_MAX - 1,
                'zero': 0,
                'negative_one': -1,
                'positive_one': 1
            },
            'float': {
                'min': FLOAT_MIN,
                'max': FLOAT_MAX,
                'min_plus_epsilon': FLOAT_MIN + 1e-6,
                'max_minus_epsilon': FLOAT_MAX - 1e-6,
                'zero': 0.0,
                'negative_one': -1.0,
                'positive_one': 1.0
            },
            'string': {
                'empty': '',
                'single_char': 'a',
                'max_length': 'a' * 1000,
                'null_terminated': 'test\0',
                'special_chars': '!@#$%^&*()'
            },
            'bool': {
                'true': True,
                'false': False
            },
            'char': {
                'null': '\0',
                'newline': '\n',
                'space': ' ',
                'min_char': '\x00',
                'max_char': '\xff'
            }
        }
    
    def generate_bva_tests(self, parameters: List[ParameterAnalysis]) -> List[BVATestScenario]:
        """
        Parametreler için BVA test senaryoları üret
        
        Args:
            parameters: Analiz edilmiş parametreler
            
        Returns:
            BVA test senaryoları listesi
        """
        self.logger.info("BVA test senaryoları üretiliyor")
        
        test_scenarios = []
        
        # Her parametre için BVA değerleri üret
        for param in parameters:
            param_tests = self._generate_parameter_bva_tests(param)
            test_scenarios.extend(param_tests)
        
        # Kombinasyon testleri üret
        combination_tests = self._generate_combination_tests(parameters)
        test_scenarios.extend(combination_tests)
        
        self.logger.info(f"{len(test_scenarios)} BVA test senaryosu üretildi")
        return test_scenarios
    
    def _generate_parameter_bva_tests(self, param: ParameterAnalysis) -> List[BVATestScenario]:
        """
        Tek parametre için BVA test değerleri üret
        
        Args:
            param: Parametre analizi
            
        Returns:
            BVA test senaryoları
        """
        tests = []
        
        # LLM analizinden gelen sınır değerlerini kullan (zorunlu)
        if param.boundary_values:
            for i, boundary_value in enumerate(param.boundary_values):
                # Beklenen sonucu hesapla
                expected_output = self._calculate_expected_output(boundary_value, param)
                
                test = BVATestScenario(
                    name=f"BVA_{param.name}_boundary_{i}",
                    description=f"BVA test for {param.name} with boundary value: {boundary_value}",
                    input_values={param.name: boundary_value},
                    expected_output=expected_output,
                    boundary_values={param.name: "boundary"}
                )
                tests.append(test)
        elif param.valid_range:
            # Valid range varsa onu kullan
            range_tests = self._generate_range_bva_tests(param)
            tests.extend(range_tests)
        else:
            # LLM analizi eksikse hata ver
            self.logger.error(f"Parametre {param.name} için LLM analizi eksik! Boundary values veya valid_range bulunamadı.")
            raise ValueError(f"LLM analizi zorunlu! Parametre {param.name} için yeterli analiz bulunamadı.")
        
        return tests
    
    def _calculate_expected_output(self, boundary_value: Any, param: ParameterAnalysis) -> Any:
        """
        Sınır değeri için beklenen sonucu hesapla
        
        Args:
            boundary_value: Sınır değeri
            param: Parametre analizi
            
        Returns:
            Beklenen sonuç
        """
        # Sınır değerinin geçerli olup olmadığını kontrol et
        if param.valid_range:
            valid_range = param.valid_range
            if 'min' in valid_range and 'max' in valid_range:
                min_val = valid_range['min']
                max_val = valid_range['max']
                
                # Sınır değeri geçerli aralıkta mı?
                if min_val <= boundary_value <= max_val:
                    # Burada fonksiyon mantığına göre gerçek sonuç hesaplanmalı
                    # Şimdilik boundary_value'yu döndür
                    return boundary_value
                else:
                    return 'error'
        
        # Geçerli aralık yoksa varsayılan olarak boundary_value'yu döndür
        return boundary_value
    
    def _generate_default_bva_tests(self, param: ParameterAnalysis) -> List[BVATestScenario]:
        """
        Varsayılan sınır değerleriyle BVA testleri üret
        
        Args:
            param: Parametre analizi
            
        Returns:
            BVA test senaryoları
        """
        tests = []
        param_type = param.type.lower()
        
        # Veri tipine göre sınır değerlerini al
        if param_type in self.boundary_values:
            boundaries = self.boundary_values[param_type]
            
            # Minimum değer
            test = BVATestScenario(
                name=f"BVA_{param.name}_min",
                description=f"BVA test for {param.name} with minimum value: {boundaries['min']}",
                input_values={param.name: boundaries['min']},
                expected_output="success",
                boundary_values={param.name: "min"}
            )
            tests.append(test)
            
            # Minimum - 1
            test = BVATestScenario(
                name=f"BVA_{param.name}_min_minus_1",
                description=f"BVA test for {param.name} with min-1 value: {boundaries['min_minus_1']}",
                input_values={param.name: boundaries['min_minus_1']},
                expected_output="error",
                boundary_values={param.name: "min_minus_1"}
            )
            tests.append(test)
            
            # Maximum değer
            test = BVATestScenario(
                name=f"BVA_{param.name}_max",
                description=f"BVA test for {param.name} with maximum value: {boundaries['max']}",
                input_values={param.name: boundaries['max']},
                expected_output="success",
                boundary_values={param.name: "max"}
            )
            tests.append(test)
            
            # Maximum + 1
            test = BVATestScenario(
                name=f"BVA_{param.name}_max_plus_1",
                description=f"BVA test for {param.name} with max+1 value: {boundaries['max_plus_1']}",
                input_values={param.name: boundaries['max_plus_1']},
                expected_output="error",
                boundary_values={param.name: "max_plus_1"}
            )
            tests.append(test)
            
            # Nominal değer (ortada)
            nominal = (boundaries['min'] + boundaries['max']) // 2
            test = BVATestScenario(
                name=f"BVA_{param.name}_nominal",
                description=f"BVA test for {param.name} with nominal value: {nominal}",
                input_values={param.name: nominal},
                expected_output="success",
                boundary_values={param.name: "nominal"}
            )
            tests.append(test)
        
        return tests
    
    def _generate_range_bva_tests(self, param: ParameterAnalysis) -> List[BVATestScenario]:
        """
        Özel aralıklar için BVA testleri üret
        
        Args:
            param: Parametre analizi
            
        Returns:
            BVA test senaryoları
        """
        tests = []
        valid_range = param.valid_range
        
        if not valid_range or 'min' not in valid_range or 'max' not in valid_range:
            return tests
        
        min_val = valid_range['min']
        max_val = valid_range['max']
        
        # Minimum değer
        test = BVATestScenario(
            name=f"BVA_{param.name}_range_min",
            description=f"BVA test for {param.name} with range minimum: {min_val}",
            input_values={param.name: min_val},
            expected_output="success",
            boundary_values={param.name: "range_min"}
        )
        tests.append(test)
        
        # Minimum - 1
        if isinstance(min_val, (int, float)):
            min_minus_1 = min_val - 1
            test = BVATestScenario(
                name=f"BVA_{param.name}_range_min_minus_1",
                description=f"BVA test for {param.name} with range min-1: {min_minus_1}",
                input_values={param.name: min_minus_1},
                expected_output="error",
                boundary_values={param.name: "range_min_minus_1"}
            )
            tests.append(test)
        
        # Maximum değer
        test = BVATestScenario(
            name=f"BVA_{param.name}_range_max",
            description=f"BVA test for {param.name} with range maximum: {max_val}",
            input_values={param.name: max_val},
            expected_output="success",
            boundary_values={param.name: "range_max"}
        )
        tests.append(test)
        
        # Maximum + 1
        if isinstance(max_val, (int, float)):
            max_plus_1 = max_val + 1
            test = BVATestScenario(
                name=f"BVA_{param.name}_range_max_plus_1",
                description=f"BVA test for {param.name} with range max+1: {max_plus_1}",
                input_values={param.name: max_plus_1},
                expected_output="error",
                boundary_values={param.name: "range_max_plus_1"}
            )
            tests.append(test)
        
        # Nominal değer
        if isinstance(min_val, (int, float)) and isinstance(max_val, (int, float)):
            nominal = (min_val + max_val) / 2
            test = BVATestScenario(
                name=f"BVA_{param.name}_range_nominal",
                description=f"BVA test for {param.name} with range nominal: {nominal}",
                input_values={param.name: nominal},
                expected_output="success",
                boundary_values={param.name: "range_nominal"}
            )
            tests.append(test)
        
        return tests
    
    def _generate_combination_tests(self, parameters: List[ParameterAnalysis]) -> List[BVATestScenario]:
        """
        Parametre kombinasyonları için BVA testleri üret
        
        Args:
            parameters: Parametre listesi
            
        Returns:
            BVA test senaryoları
        """
        tests = []
        
        if len(parameters) < 2:
            return tests
        
        # İki parametre kombinasyonları
        for i in range(len(parameters)):
            for j in range(i + 1, len(parameters)):
                param1 = parameters[i]
                param2 = parameters[j]
                
                # Her iki parametre için minimum değerler
                test = BVATestScenario(
                    name=f"BVA_{param1.name}_{param2.name}_both_min",
                    description=f"BVA test for {param1.name} and {param2.name} with minimum values",
                    input_values={
                        param1.name: self._get_min_value(param1),
                        param2.name: self._get_min_value(param2)
                    },
                    expected_output="success",
                    boundary_values={
                        param1.name: "min",
                        param2.name: "min"
                    }
                )
                tests.append(test)
                
                # Her iki parametre için maximum değerler
                test = BVATestScenario(
                    name=f"BVA_{param1.name}_{param2.name}_both_max",
                    description=f"BVA test for {param1.name} and {param2.name} with maximum values",
                    input_values={
                        param1.name: self._get_max_value(param1),
                        param2.name: self._get_max_value(param2)
                    },
                    expected_output="success",
                    boundary_values={
                        param1.name: "max",
                        param2.name: "max"
                    }
                )
                tests.append(test)
                
                # İlk parametre minimum, ikinci maximum
                test = BVATestScenario(
                    name=f"BVA_{param1.name}_min_{param2.name}_max",
                    description=f"BVA test for {param1.name} min and {param2.name} max",
                    input_values={
                        param1.name: self._get_min_value(param1),
                        param2.name: self._get_max_value(param2)
                    },
                    expected_output="success",
                    boundary_values={
                        param1.name: "min",
                        param2.name: "max"
                    }
                )
                tests.append(test)
        
        return tests
    
    def _get_min_value(self, param: ParameterAnalysis) -> Any:
        """
        Parametre için minimum değer al
        
        Args:
            param: Parametre analizi
            
        Returns:
            Minimum değer
        """
        if param.valid_range and 'min' in param.valid_range:
            return param.valid_range['min']
        
        param_type = param.type.lower()
        if param_type in self.boundary_values:
            return self.boundary_values[param_type]['min']
        
        return 0
    
    def _get_max_value(self, param: ParameterAnalysis) -> Any:
        """
        Parametre için maximum değer al
        
        Args:
            param: Parametre analizi
            
        Returns:
            Maximum değer
        """
        if param.valid_range and 'max' in param.valid_range:
            return param.valid_range['max']
        
        param_type = param.type.lower()
        if param_type in self.boundary_values:
            return self.boundary_values[param_type]['max']
        
        return 100
    
    def generate_string_bva_tests(self, param: ParameterAnalysis) -> List[BVATestScenario]:
        """
        String parametreler için BVA testleri üret
        
        Args:
            param: String parametre analizi
            
        Returns:
            BVA test senaryoları
        """
        tests = []
        
        # Boş string
        test = BVATestScenario(
            name=f"BVA_{param.name}_empty_string",
            description=f"BVA test for {param.name} with empty string",
            input_values={param.name: ""},
            expected_output="success",
            boundary_values={param.name: "empty"}
        )
        tests.append(test)
        
        # Tek karakter
        test = BVATestScenario(
            name=f"BVA_{param.name}_single_char",
            description=f"BVA test for {param.name} with single character",
            input_values={param.name: "a"},
            expected_output="success",
            boundary_values={param.name: "single_char"}
        )
        tests.append(test)
        
        # Çok uzun string
        long_string = "a" * 1000
        test = BVATestScenario(
            name=f"BVA_{param.name}_long_string",
            description=f"BVA test for {param.name} with long string",
            input_values={param.name: long_string},
            expected_output="success",
            boundary_values={param.name: "long"}
        )
        tests.append(test)
        
        # Null pointer
        test = BVATestScenario(
            name=f"BVA_{param.name}_null_pointer",
            description=f"BVA test for {param.name} with null pointer",
            input_values={param.name: None},
            expected_output="error",
            boundary_values={param.name: "null"}
        )
        tests.append(test)
        
        return tests 