"""
Base chunking strategy
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..models import CodeChunk, ChunkType


class ChunkingStrategy(ABC):
    """Base class for chunking strategies"""
    
    @abstractmethod
    def chunk(self, code: str, language: str) -> List[CodeChunk]:
        """Chunk the code"""
        pass
    
    @abstractmethod
    def should_split(self, chunk: CodeChunk) -> bool:
        """Determine if chunk should be split"""
        pass
    
    @abstractmethod
    def merge_small_chunks(self, chunks: List[CodeChunk]) -> List[CodeChunk]:
        """Merge chunks that are too small"""
        pass
