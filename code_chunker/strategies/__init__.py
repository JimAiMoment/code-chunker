"""
Chunking strategies for code-chunker
"""

from .base import ChunkingStrategy
from .default import DefaultChunkingStrategy

__all__ = [
    'ChunkingStrategy',
    'DefaultChunkingStrategy'
]
