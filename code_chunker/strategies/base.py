"""
Base chunking strategy
"""

from abc import ABC, abstractmethod
from typing import List

from ..models import CodeChunk


class ChunkingStrategy(ABC):
    """分塊策略基類"""
    
    @abstractmethod
    def chunk(self, code: str, language: str) -> List[CodeChunk]:
        """將程式碼分塊"""
        pass
    
    @abstractmethod
    def should_split(self, chunk: CodeChunk) -> bool:
        """決定是否應該分割chunk"""
        pass
    
    @abstractmethod
    def merge_chunks(self, chunks: List[CodeChunk]) -> List[CodeChunk]:
        """合併太小的chunks"""
        pass
