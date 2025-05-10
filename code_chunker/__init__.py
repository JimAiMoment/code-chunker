"""
Code Chunker - A pragmatic multi-language code parser for LLM applications
"""

from .__version__ import __version__
from .chunker import CodeChunker
from .models import CodeChunk, ParseResult, Import, ChunkType, ChunkerConfig

__all__ = [
    '__version__',
    'CodeChunker',
    'CodeChunk',
    'ParseResult',
    'Import',
    'ChunkType',
    'ChunkerConfig'
]
