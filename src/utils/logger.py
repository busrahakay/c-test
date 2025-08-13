"""
Logging utility'si
"""

import sys
from pathlib import Path
from loguru import logger
from typing import Optional


def setup_logger(
    log_file: Optional[Path] = None,
    level: str = "INFO",
    format: str = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
) -> None:
    """
    Logger'ı yapılandır
    
    Args:
        log_file: Log dosyası yolu
        level: Log seviyesi
        format: Log formatı
    """
    # Mevcut logger'ları temizle
    logger.remove()
    
    # Console logger'ı ekle
    logger.add(
        sys.stderr,
        format=format,
        level=level,
        colorize=True
    )
    
    # Dosya logger'ı ekle (eğer belirtilmişse)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        logger.add(
            log_file,
            format=format,
            level=level,
            rotation="10 MB",
            retention="7 days",
            compression="zip"
        )


def get_logger(name: str = __name__):
    """
    Logger instance'ı al
    
    Args:
        name: Logger adı
        
    Returns:
        Logger instance'ı
    """
    return logger.bind(name=name)


# Varsayılan logger setup'ı
setup_logger() 