"""
Default chunking strategy
"""

from typing import List

from .base import ChunkingStrategy
from ..models import CodeChunk, ChunkerConfig


class DefaultChunkingStrategy(ChunkingStrategy):
    """Default chunking strategy"""
    
    def __init__(self, config: ChunkerConfig):
        self.config = config
    
    def chunk(self, code: str, language: str) -> List[CodeChunk]:
        """Chunk code using default strategy"""
        # This method will be overridden in the parser
        return []
    
    def should_split(self, chunk: CodeChunk) -> bool:
        """Determine if chunk should be split"""
        return False
    
    def merge_small_chunks(self, chunks: List[CodeChunk]) -> List[CodeChunk]:
        """Merge chunks that are too small"""
        if not chunks:
            return []
        
        # Merge chunks
        merged = []
        current = chunks[0]
        
        for next_chunk in chunks[1:]:
            if self._should_merge(current, next_chunk):
                current = self._merge_chunks(current, next_chunk)
            else:
                merged.append(current)
                current = next_chunk
        
        merged.append(current)
        return merged
    
    def _should_merge(self, chunk1: CodeChunk, chunk2: CodeChunk) -> bool:
        """Determine if two chunks should be merged"""
        return (
            chunk1.type == chunk2.type and
            chunk2.start_line - chunk1.end_line <= 1
        )
    
    def _merge_chunks(self, chunk1: CodeChunk, chunk2: CodeChunk) -> CodeChunk:
        """Merge two chunks"""
        return CodeChunk(
            type=chunk1.type,
            name=chunk1.name,
            code=chunk1.code + '\n' + chunk2.code,
            start_line=chunk1.start_line,
            end_line=chunk2.end_line,
            language=chunk1.language,
            confidence=min(chunk1.confidence, chunk2.confidence),
            metadata={**chunk1.metadata, **chunk2.metadata}
        )
