"""
Default chunking strategy
"""

from typing import List

from .base import ChunkingStrategy
from ..models import CodeChunk, ChunkerConfig


class DefaultChunkingStrategy(ChunkingStrategy):
    """預設分塊策略"""
    
    def __init__(self, config: ChunkerConfig):
        self.config = config
    
    def chunk(self, code: str, language: str) -> List[CodeChunk]:
        """使用預設策略分塊"""
        # 這個方法將在parser中被覆寫
        return []
    
    def should_split(self, chunk: CodeChunk) -> bool:
        """決定是否應該分割chunk"""
        return len(chunk.code) > self.config.max_chunk_size
    
    def merge_chunks(self, chunks: List[CodeChunk]) -> List[CodeChunk]:
        """合併太小的chunks"""
        if not chunks:
            return []
        
        merged = []
        current = chunks[0]
        
        for chunk in chunks[1:]:
            if (len(current.code) + len(chunk.code) < self.config.max_chunk_size and
                chunk.start_line - current.end_line <= 1):
                # 合併chunks
                current = CodeChunk(
                    type=current.type,
                    name=f"{current.name}_{chunk.name}" if current.name and chunk.name else None,
                    code=current.code + '\n' + chunk.code,
                    start_line=current.start_line,
                    end_line=chunk.end_line,
                    language=current.language,
                    confidence=min(current.confidence, chunk.confidence)
                )
            else:
                merged.append(current)
                current = chunk
        
        merged.append(current)
        return merged
