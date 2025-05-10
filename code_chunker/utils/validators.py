"""
Validation utilities
"""

from typing import Set

from ..models import ChunkerConfig
from ..exceptions import ChunkerError


SUPPORTED_LANGUAGES: Set[str] = {
    'python', 'javascript', 'typescript', 'solidity', 'go', 'rust'
}


def validate_config(config: ChunkerConfig) -> None:
    """Validate configuration"""
    if config.max_chunk_size <= 0:
        raise ChunkerError("max_chunk_size must be positive")
    
    if config.min_chunk_size < 0:
        raise ChunkerError("min_chunk_size must be non-negative")
    
    if config.min_chunk_size >= config.max_chunk_size:
        raise ChunkerError("min_chunk_size must be less than max_chunk_size")
    
    if config.overlap_size < 0:
        raise ChunkerError("overlap_size must be non-negative")
    
    if config.confidence_threshold < 0 or config.confidence_threshold > 1:
        raise ChunkerError("confidence_threshold must be between 0 and 1")


def validate_language(language: str) -> None:
    """Validate if language is supported"""
    if language not in SUPPORTED_LANGUAGES:
        raise ChunkerError(f"Language '{language}' is not supported. Supported languages: {', '.join(SUPPORTED_LANGUAGES)}")
