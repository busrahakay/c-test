"""
Equivalence Partitioning (EP) test değerleri üreten modül
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import random
import sys

from ..analyzer.llm_analyzer import ParameterAnalysis
from ..utils.logger import get_logger

logger = get_logger(__name__)

# C sabitleri
INT_MIN = -2147483648
INT_MAX = 2147483647
FLOAT_MIN = -3.402823e+38
FLOAT_MAX = 3.402823e+38


@dataclass
class EPTestValue:
    """EP test değeri"""
    value: Any
    description: str
    equivalence_class: str
    expected_behavior: str
    is_valid: bool


@dataclass
class EPTestScenario:
    """EP test senaryosu"""
    name: str
    description: str
    input_values: Dict[str, Any]
    expected_output: Any
    equivalence_classes: Dict[str, str]
    test_type: str = "EP"


class EPGenerator:
    """Equivalence Partitioning test değerleri üreten sınıf"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        
        # Veri tipi bazlı varsayılan değerler
        self.default_values = {
            'int': {
                'valid': [0, 1, 100, -1, -100, INT_MIN, INT_MAX],
                'invalid': [None, 'abc', 3.14],
                'boundaries': [INT_MIN, -1, 0, 1, INT_MAX]
            },
            'float': {
                'valid': [0.0, 1.0, -1.0, 3.14, -3.14, FLOAT_MIN, FLOAT_MAX],
                'invalid': [None, 'abc', ''],
                'boundaries': [FLOAT_MIN, -1.0, 0.0, 1.0, FLOAT_MAX]
            },
            'string': {
                'valid': ['', 'test', 'hello world', 'a'],
                'invalid': [None, 123, 3.14],
                'boundaries': ['', 'a' * 1000]
            },
            'bool': {
                'valid': [True, False],
                'invalid': [None, 0, 1, 'true', 'false'],
                'boundaries': [True, False]
            },
            'char': {
                'valid': ['a', 'Z', '0', '9', ' '],
                'invalid': [None, '', 'ab', 65],
                'boundaries': ['\0', '\n', ' ']
            }
        }
    
    def generate_ep_tests(self, parameters: List[ParameterAnalysis]) -> List[EPTestScenario]:
        """
        Parametreler için EP test senaryoları üret
        
        Args:
            parameters: Analiz edilmiş parametreler
            
        Returns:
            EP test senaryoları listesi
        """
        self.logger.info("EP test senaryoları üretiliyor")
        
        test_scenarios = []
        
        # Her parametre için EP değerleri üret
        for param in parameters:
            param_tests = self._generate_parameter_ep_tests(param)
            test_scenarios.extend(param_tests)
        
        # Kombinasyon testleri üret
        combination_tests = self._generate_combination_tests(parameters)
        test_scenarios.extend(combination_tests)
        
        self.logger.info(f"{len(test_scenarios)} EP test senaryosu üretildi")
        return test_scenarios
    
    def _generate_parameter_ep_tests(self, param: ParameterAnalysis) -> List[EPTestScenario]:
        """
        Tek parametre için EP test değerleri üret
        
        Args:
            param: Parametre analizi
            
        Returns:
            EP test senaryoları
        """
        tests = []
        
        # LLM analizinden gelen eşdeğerlik sınıflarını kullan (zorunlu)
        if param.equivalence_classes:
            for eq_class in param.equivalence_classes:
                # Beklenen sonucu hesapla
                expected_output = self._calculate_expected_output(eq_class)
                
                test = EPTestScenario(
                    name=f"EP_{param.name}_{eq_class['name']}",
                    description=f"EP test for {param.name}: {eq_class['description']}",
                    input_values={param.name: eq_class['representative_value']},
                    expected_output=expected_output,
                    equivalence_classes={param.name: eq_class['name']}
                )
                tests.append(test)
        elif param.valid_range:
            # Valid range varsa onu kullan
            range_tests = self._generate_range_based_tests(param)
            tests.extend(range_tests)
        else:
            # LLM analizi eksikse hata ver
            self.logger.error(f"Parametre {param.name} için LLM analizi eksik! Equivalence classes veya valid_range bulunamadı.")
            raise ValueError(f"LLM analizi zorunlu! Parametre {param.name} için yeterli analiz bulunamadı.")
        
        return tests
    
    def _calculate_expected_output(self, eq_class: Dict[str, Any]) -> Any:
        """
        Eşdeğerlik sınıfı için beklenen sonucu hesapla
        
        Args:
            eq_class: Eşdeğerlik sınıfı
            
        Returns:
            Beklenen sonuç
        """
        # LLM'den gelen expected_output varsa onu kullan
        if 'expected_output' in eq_class and eq_class['expected_output'] != 'error':
            return eq_class['expected_output']
        
        # Fonksiyon mantığına göre hesapla
        # Bu kısım fonksiyon tipine göre genişletilebilir
        if 'expected_behavior' in eq_class:
            behavior = eq_class['expected_behavior'].lower()
            if 'error' in behavior or 'invalid' in behavior:
                return 'error'
            elif 'success' in behavior or 'valid' in behavior:
                # Burada fonksiyon mantığına göre gerçek sonuç hesaplanmalı
                # Şimdilik representative_value'yu döndür
                return eq_class.get('representative_value', 'success')
        
        return 'success'
    
    def _generate_range_based_tests(self, param: ParameterAnalysis) -> List[EPTestScenario]:
        """
        Valid range kullanarak EP testleri üret
        
        Args:
            param: Parametre analizi
            
        Returns:
            EP test senaryoları
        """
        tests = []
        
        if not param.valid_range:
            return tests
            
        valid_range = param.valid_range
        
        # Geçerli aralık içinde değer
        if 'min' in valid_range and 'max' in valid_range:
            mid_value = (valid_range['min'] + valid_range['max']) // 2
            test = EPTestScenario(
                name=f"EP_{param.name}_valid_range",
                description=f"EP test for {param.name} within valid range: {valid_range['min']} to {valid_range['max']}",
                input_values={param.name: mid_value},
                expected_output="success",
                equivalence_classes={param.name: "valid_range"}
            )
            tests.append(test)
        
        # Geçersiz değerler (range dışında)
        if 'min' in valid_range:
            invalid_min = valid_range['min'] - 1
            test = EPTestScenario(
                name=f"EP_{param.name}_invalid_below_min",
                description=f"EP test for {param.name} below minimum: {invalid_min}",
                input_values={param.name: invalid_min},
                expected_output="error",
                equivalence_classes={param.name: "invalid_below_min"}
            )
            tests.append(test)
            
        if 'max' in valid_range:
            invalid_max = valid_range['max'] + 1
            test = EPTestScenario(
                name=f"EP_{param.name}_invalid_above_max",
                description=f"EP test for {param.name} above maximum: {invalid_max}",
                input_values={param.name: invalid_max},
                expected_output="error",
                equivalence_classes={param.name: "invalid_above_max"}
            )
            tests.append(test)
        
        return tests
    
    def _generate_default_ep_tests(self, param: ParameterAnalysis) -> List[EPTestScenario]:
        """
        Varsayılan değerlerle EP testleri üret
        
        Args:
            param: Parametre analizi
            
        Returns:
            EP test senaryoları
        """
        tests = []
        param_type = param.type.lower()
        
        # Veri tipine göre varsayılan değerleri al
        if param_type in self.default_values:
            defaults = self.default_values[param_type]
            
            # Geçerli değerler için testler
            for i, value in enumerate(defaults['valid']):
                test = EPTestScenario(
                    name=f"EP_{param.name}_valid_{i}",
                    description=f"EP test for {param.name} with valid value: {value}",
                    input_values={param.name: value},
                    expected_output="success",
                    equivalence_classes={param.name: "valid"}
                )
                tests.append(test)
            
            # Geçersiz değerler için testler
            for i, value in enumerate(defaults['invalid']):
                test = EPTestScenario(
                    name=f"EP_{param.name}_invalid_{i}",
                    description=f"EP test for {param.name} with invalid value: {value}",
                    input_values={param.name: value},
                    expected_output="error",
                    equivalence_classes={param.name: "invalid"}
                )
                tests.append(test)
        
        # Özel kısıtlamalar için testler
        if param.constraints:
            constraint_tests = self._generate_constraint_tests(param)
            tests.extend(constraint_tests)
        
        return tests
    
    def _generate_constraint_tests(self, param: ParameterAnalysis) -> List[EPTestScenario]:
        """
        Kısıtlamalar için EP testleri üret
        
        Args:
            param: Parametre analizi
            
        Returns:
            EP test senaryoları
        """
        tests = []
        
        for constraint in param.constraints:
            # Kısıtlama tipini analiz et
            if "positive" in constraint.lower() or "> 0" in constraint:
                # Pozitif değerler
                test = EPTestScenario(
                    name=f"EP_{param.name}_positive",
                    description=f"EP test for {param.name} with positive value",
                    input_values={param.name: 1},
                    expected_output="success",
                    equivalence_classes={param.name: "positive"}
                )
                tests.append(test)
                
                # Negatif değerler
                test = EPTestScenario(
                    name=f"EP_{param.name}_negative",
                    description=f"EP test for {param.name} with negative value",
                    input_values={param.name: -1},
                    expected_output="error",
                    equivalence_classes={param.name: "negative"}
                )
                tests.append(test)
            
            elif "non-zero" in constraint.lower() or "!= 0" in constraint:
                # Sıfır olmayan değerler
                test = EPTestScenario(
                    name=f"EP_{param.name}_nonzero",
                    description=f"EP test for {param.name} with non-zero value",
                    input_values={param.name: 1},
                    expected_output="success",
                    equivalence_classes={param.name: "nonzero"}
                )
                tests.append(test)
                
                # Sıfır değer
                test = EPTestScenario(
                    name=f"EP_{param.name}_zero",
                    description=f"EP test for {param.name} with zero value",
                    input_values={param.name: 0},
                    expected_output="error",
                    equivalence_classes={param.name: "zero"}
                )
                tests.append(test)
            
            elif "non-null" in constraint.lower() or "!= null" in constraint:
                # Null olmayan değerler
                test = EPTestScenario(
                    name=f"EP_{param.name}_nonnull",
                    description=f"EP test for {param.name} with non-null value",
                    input_values={param.name: "test"},
                    expected_output="success",
                    equivalence_classes={param.name: "nonnull"}
                )
                tests.append(test)
                
                # Null değer
                test = EPTestScenario(
                    name=f"EP_{param.name}_null",
                    description=f"EP test for {param.name} with null value",
                    input_values={param.name: None},
                    expected_output="error",
                    equivalence_classes={param.name: "null"}
                )
                tests.append(test)
        
        return tests
    
    def _generate_combination_tests(self, parameters: List[ParameterAnalysis]) -> List[EPTestScenario]:
        """
        Parametre kombinasyonları için EP testleri üret
        
        Args:
            parameters: Parametre listesi
            
        Returns:
            EP test senaryoları
        """
        tests = []
        
        if len(parameters) < 2:
            return tests
        
        # İki parametre kombinasyonları
        for i in range(len(parameters)):
            for j in range(i + 1, len(parameters)):
                param1 = parameters[i]
                param2 = parameters[j]
                
                # Her iki parametre için geçerli değerler
                test = EPTestScenario(
                    name=f"EP_{param1.name}_{param2.name}_both_valid",
                    description=f"EP test for {param1.name} and {param2.name} with valid values",
                    input_values={
                        param1.name: self._get_representative_value(param1),
                        param2.name: self._get_representative_value(param2)
                    },
                    expected_output="success",
                    equivalence_classes={
                        param1.name: "valid",
                        param2.name: "valid"
                    }
                )
                tests.append(test)
                
                # İlk parametre geçerli, ikinci geçersiz
                test = EPTestScenario(
                    name=f"EP_{param1.name}_valid_{param2.name}_invalid",
                    description=f"EP test for {param1.name} valid and {param2.name} invalid",
                    input_values={
                        param1.name: self._get_representative_value(param1),
                        param2.name: self._get_invalid_value(param2)
                    },
                    expected_output="error",
                    equivalence_classes={
                        param1.name: "valid",
                        param2.name: "invalid"
                    }
                )
                tests.append(test)
        
        return tests
    
    def _get_representative_value(self, param: ParameterAnalysis) -> Any:
        """
        Parametre için temsilci değer al
        
        Args:
            param: Parametre analizi
            
        Returns:
            Temsilci değer
        """
        if param.equivalence_classes:
            return param.equivalence_classes[0]['representative_value']
        
        param_type = param.type.lower()
        if param_type in self.default_values:
            return self.default_values[param_type]['valid'][0]
        
        return None
    
    def _get_invalid_value(self, param: ParameterAnalysis) -> Any:
        """
        Parametre için geçersiz değer al
        
        Args:
            param: Parametre analizi
            
        Returns:
            Geçersiz değer
        """
        if param.invalid_values:
            return param.invalid_values[0]
        
        param_type = param.type.lower()
        if param_type in self.default_values:
            return self.default_values[param_type]['invalid'][0]
        
        return None 