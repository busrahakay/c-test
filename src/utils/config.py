"""
Proje konfigürasyonu ve ayarları
"""

import os
from typing import Dict, Any
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

@dataclass
class LLMConfig:
    """LLM konfigürasyonu"""
    api_key: str = "OPENAI_API_KEY"
    model: str = "deepseek/deepseek-chat-v3-0324:free"
    temperature: float = 0.1
    max_tokens: int = 2000


@dataclass
class TestConfig:
    """Test üretimi konfigürasyonu"""
    framework: str = "unity"  # unity, cmocka, custom
    output_dir: str = "generated_tests"
    include_ep: bool = True
    include_bva: bool = True
    max_test_cases: int = 50


@dataclass
class ParserConfig:
    """Parser konfigürasyonu"""
    doxygen_tags: list = None
    c_standard: str = "c99"
    include_paths: list = None
    
    def __post_init__(self):
        if self.doxygen_tags is None:
            self.doxygen_tags = [
                "@param", "@return", "@brief", "@details", 
                "@pre", "@post", "@throws", "@note", "@warning"
            ]
        if self.include_paths is None:
            self.include_paths = []


class Config:
    """Ana konfigürasyon sınıfı"""
    
    def __init__(self):
        self.llm = LLMConfig()
        self.test = TestConfig()
        self.parser = ParserConfig()
        
        # Proje yolları
        self.project_root = Path(__file__).parent.parent.parent
        self.src_dir = self.project_root / "src"
        self.examples_dir = self.project_root / "examples"
        self.tests_dir = self.project_root / "tests"
        
    def validate(self) -> bool:
        """Konfigürasyonu doğrula"""
        # LLM model kontrolü
        if not self.llm.model:
            raise ValueError("LLM model is required")
            
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Konfigürasyonu dictionary'e çevir"""
        return {
            "llm": {
                "model": self.llm.model,
                "temperature": self.llm.temperature,
                "max_tokens": self.llm.max_tokens
            },
            "test": {
                "framework": self.test.framework,
                "output_dir": self.test.output_dir,
                "include_ep": self.test.include_ep,
                "include_bva": self.test.include_bva,
                "max_test_cases": self.test.max_test_cases
            },
            "parser": {
                "c_standard": self.parser.c_standard,
                "doxygen_tags": self.parser.doxygen_tags,
                "include_paths": self.parser.include_paths
            }
        }


# Global config instance
config = Config() 