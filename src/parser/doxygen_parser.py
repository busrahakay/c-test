"""
Doxygen formatındaki C fonksiyonlarını parse eden modül
"""

import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class DoxygenParam:
    """Doxygen parametre bilgisi"""
    name: str
    description: str
    type: Optional[str] = None
    direction: Optional[str] = None  # in, out, inout


@dataclass
class DoxygenReturn:
    """Doxygen return bilgisi"""
    description: str
    type: Optional[str] = None


@dataclass
class DoxygenPrecondition:
    """Doxygen önkoşul bilgisi"""
    description: str


@dataclass
class DoxygenPostcondition:
    """Doxygen sonkoşul bilgisi"""
    description: str


@dataclass
class DoxygenFunction:
    """Doxygen fonksiyon bilgisi"""
    name: str
    signature: str
    brief: str
    details: Optional[str] = None
    params: List[DoxygenParam] = None
    return_info: Optional[DoxygenReturn] = None
    preconditions: List[DoxygenPrecondition] = None
    postconditions: List[DoxygenPostcondition] = None
    notes: List[str] = None
    warnings: List[str] = None
    throws: List[str] = None
    code: Optional[str] = None
    
    def __post_init__(self):
        if self.params is None:
            self.params = []
        if self.preconditions is None:
            self.preconditions = []
        if self.postconditions is None:
            self.postconditions = []
        if self.notes is None:
            self.notes = []
        if self.warnings is None:
            self.warnings = []
        if self.throws is None:
            self.throws = []


class DoxygenParser:
    """Doxygen formatındaki C fonksiyonlarını parse eden sınıf"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        
        # Doxygen tag regex pattern'leri
        self.patterns = {
            'function_start': r'/\*\*\s*$',
            'function_end': r'\*/\s*$',
            'brief': r'@brief\s+(.+)$',
            'details': r'@details\s+(.+)$',
            'param': r'@param\s+(\w+)\s+(.+)$',
            'param_with_type': r'@param\s+\[(in|out|inout)\]\s+(\w+)\s+(.+)$',
            'return': r'@return\s+(.+)$',
            'pre': r'@pre\s+(.+)$',
            'post': r'@post\s+(.+)$',
            'note': r'@note\s+(.+)$',
            'warning': r'@warning\s+(.+)$',
            'throws': r'@throws\s+(.+)$',
            'function_signature': r'(?:const\s+)?(?:char\s*\*|int|void|float|double|long|short|unsigned|signed)\s+(\w+(?:_\w+)*)\s*\([^)]*\)\s*;?\s*$',
            'simple_function': r'(?:const\s+)?(?:char\s*\*|int|void|float|double|long|short|unsigned|signed)\s+(\w+(?:_\w+)*)\s*\([^)]*\)\s*\{'
        }
        
        # Regex pattern'leri compile et
        self.compiled_patterns = {
            key: re.compile(pattern, re.MULTILINE | re.IGNORECASE)
            for key, pattern in self.patterns.items()
        }
    
    def parse_file(self, file_path: Path) -> List[DoxygenFunction]:
        """
        Dosyadaki tüm Doxygen fonksiyonlarını parse et
        
        Args:
            file_path: C dosyası yolu
            
        Returns:
            Parse edilmiş fonksiyon listesi
        """
        self.logger.info(f"Dosya parse ediliyor: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.logger.error(f"Dosya okunamadı: {e}")
            return []
        
        return self.parse_content(content)
    
    def parse_content(self, content: str) -> List[DoxygenFunction]:
        """
        İçerikteki Doxygen fonksiyonlarını parse et
        
        Args:
            content: C dosyası içeriği
            
        Returns:
            Parse edilmiş fonksiyon listesi
        """
        functions = []
        
        # Doxygen bloklarını bul
        doxygen_blocks = self._extract_doxygen_blocks(content)
        
        for block in doxygen_blocks:
            try:
                function = self._parse_doxygen_block(block, content)
                if function:
                    functions.append(function)
            except Exception as e:
                self.logger.warning(f"Doxygen bloğu parse edilemedi: {e}")
                continue
        
        self.logger.info(f"{len(functions)} fonksiyon parse edildi")
        return functions
    
    def _extract_doxygen_blocks(self, content: str) -> List[str]:
        """
        İçerikten Doxygen bloklarını çıkar
        
        Args:
            content: C dosyası içeriği
            
        Returns:
            Doxygen blokları listesi
        """
        blocks = []
        
        # /** ile başlayan ve */ ile biten blokları bul
        pattern = r'/\*\*.*?\*/'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for match in matches:
            # @file tag'i varsa bu bir dosya açıklaması, atla
            if '@file' in match:
                continue
                
            # Doxygen bloğunun bittiği yeri bul
            match_start = content.find(match)
            match_end = match_start + len(match)
            remaining_content = content[match_end:]
            
            # Kalan içerikte fonksiyon imzasını ara (daha geniş arama)
            lines = remaining_content.split('\n')
            function_found = False
            
            for i, line in enumerate(lines):
                line = line.strip()
                # Boş satırları atla
                if not line:
                    continue
                    
                # Fonksiyon imzasını ara (daha esnek pattern)
                if (re.search(r'^\s*(?:const\s+)?(?:char\s*\*|int|void|float|double|long|short|unsigned|signed)\s+\w+\s*\([^)]*\)\s*\{?\s*$', line) or
                    re.search(r'^\s*(?:const\s+)?(?:char\s*\*|int|void|float|double|long|short|unsigned|signed)\s+\w+\s*\([^)]*\)\s*;?\s*$', line)):
                    # Doxygen bloğu ile fonksiyon arasındaki tüm satırları dahil et
                    block_with_signature = match + '\n' + '\n'.join(lines[:i+1])
                    blocks.append(block_with_signature)
                    function_found = True
                    break
            
            # Eğer fonksiyon bulunamadıysa, sadece Doxygen bloğunu ekle
            if not function_found:
                blocks.append(match)
        
        return blocks
    
    def _extract_function_code(self, content: str, signature: str) -> str:
        """
        Fonksiyon kodunu çıkar
        
        Args:
            content: C dosyası içeriği
            signature: Fonksiyon imzası
            
        Returns:
            Fonksiyon kodu
        """
        # Fonksiyon imzasının başladığı yeri bul
        start_pos = content.find(signature)
        if start_pos == -1:
            return ""
        
        # Fonksiyonun başladığı yeri bul
        brace_start = content.find('{', start_pos)
        if brace_start == -1:
            return ""
        
        # Fonksiyonun bittiği yeri bul (parantez sayarak)
        brace_count = 0
        end_pos = brace_start
        
        for i in range(brace_start, len(content)):
            if content[i] == '{':
                brace_count += 1
            elif content[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_pos = i + 1
                    break
        
        return content[start_pos:end_pos]
    
    def _parse_doxygen_block(self, block: str, content: str) -> Optional[DoxygenFunction]:
        """
        Doxygen bloğunu parse et
        
        Args:
            block: Doxygen bloğu
            content: Orijinal dosya içeriği
            
        Returns:
            Parse edilmiş fonksiyon veya None
        """
        lines = block.split('\n')
        
        # Fonksiyon imzasını bul
        signature = None
        for line in lines:
            line = line.strip()
            # Daha esnek fonksiyon imzası arama
            if (re.search(r'^\s*(?:const\s+)?(?:char\s*\*|int|void|float|double|long|short|unsigned|signed)\s+\w+\s*\([^)]*\)\s*\{?\s*$', line) or
                re.search(r'^\s*(?:const\s+)?(?:char\s*\*|int|void|float|double|long|short|unsigned|signed)\s+\w+\s*\([^)]*\)\s*;?\s*$', line)):
                signature = line.strip()
                break
        
        if not signature:
            return None
        
        # Fonksiyon adını çıkar
        # Önce return type'ı temizle
        signature_clean = re.sub(r'^\s*(?:const\s+)?(?:char\s*\*|int|void|float|double|long|short|unsigned|signed)\s+', '', signature)
        name_match = re.search(r'(\w+(?:_\w+)*)\s*\(', signature_clean)
        if not name_match:
            return None
        
        function_name = name_match.group(1)
        
        # Doxygen bilgilerini parse et
        brief = ""
        details = ""
        params = []
        return_info = None
        preconditions = []
        postconditions = []
        notes = []
        warnings = []
        throws = []
        
        for line in lines:
            line = line.strip()
            
            # @brief
            match = self.compiled_patterns['brief'].search(line)
            if match:
                brief = match.group(1).strip()
                continue
            
            # @details
            match = self.compiled_patterns['details'].search(line)
            if match:
                details = match.group(1).strip()
                continue
            
            # @param with direction (önce bunu kontrol et)
            match = self.compiled_patterns['param_with_type'].search(line)
            if match:
                direction = match.group(1)
                param_name = match.group(2)
                param_desc = match.group(3).strip()
                params.append(DoxygenParam(
                    name=param_name, 
                    description=param_desc,
                    direction=direction
                ))
                continue
            
            # @param (basit format)
            match = self.compiled_patterns['param'].search(line)
            if match:
                param_name = match.group(1)
                param_desc = match.group(2).strip()
                # Aynı parametre zaten eklenmiş mi kontrol et
                if not any(p.name == param_name for p in params):
                    params.append(DoxygenParam(name=param_name, description=param_desc))
                continue
            
            # @return
            match = self.compiled_patterns['return'].search(line)
            if match:
                return_desc = match.group(1).strip()
                return_info = DoxygenReturn(description=return_desc)
                continue
            
            # @pre
            match = self.compiled_patterns['pre'].search(line)
            if match:
                pre_desc = match.group(1).strip()
                preconditions.append(DoxygenPrecondition(description=pre_desc))
                continue
            
            # @post
            match = self.compiled_patterns['post'].search(line)
            if match:
                post_desc = match.group(1).strip()
                postconditions.append(DoxygenPostcondition(description=post_desc))
                continue
            
            # @note
            match = self.compiled_patterns['note'].search(line)
            if match:
                note = match.group(1).strip()
                notes.append(note)
                continue
            
            # @warning
            match = self.compiled_patterns['warning'].search(line)
            if match:
                warning = match.group(1).strip()
                warnings.append(warning)
                continue
            
            # @throws
            match = self.compiled_patterns['throws'].search(line)
            if match:
                throw = match.group(1).strip()
                throws.append(throw)
                continue
        
        # Fonksiyon kodunu al
        function_code = self._extract_function_code(content, signature)
        
        return DoxygenFunction(
            name=function_name,
            signature=signature,
            brief=brief,
            details=details,
            params=params,
            return_info=return_info,
            preconditions=preconditions,
            postconditions=postconditions,
            notes=notes,
            warnings=warnings,
            throws=throws,
            code=function_code
        )
    
    def get_function_info(self, function: DoxygenFunction) -> Dict[str, Any]:
        """
        Fonksiyon bilgilerini dictionary formatında döndür
        
        Args:
            function: Doxygen fonksiyonu
            
        Returns:
            Fonksiyon bilgileri dictionary'si
        """
        return {
            'name': function.name,
            'signature': function.signature,
            'brief': function.brief,
            'details': function.details,
            'params': [
                {
                    'name': param.name,
                    'description': param.description,
                    'type': param.type,
                    'direction': param.direction
                }
                for param in function.params
            ],
            'return': {
                'description': function.return_info.description if function.return_info else None,
                'type': function.return_info.type if function.return_info else None
            },
            'preconditions': [pre.description for pre in function.preconditions],
            'postconditions': [post.description for post in function.postconditions],
            'notes': function.notes,
            'warnings': function.warnings,
            'throws': function.throws,
            'code': function.code
        } 