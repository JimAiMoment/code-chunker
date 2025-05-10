"""
Semantic-aware chunking strategy
"""

from typing import List
from .base import ChunkingStrategy
from ..models import CodeChunk, ChunkType

class SemanticChunkingStrategy(ChunkingStrategy):
    """Semantic-aware chunking strategy"""
    
    def __init__(self, config):
        self.config = config
        self.related_types = {
            ChunkType.CLASS: [ChunkType.METHOD, ChunkType.FUNCTION],
            ChunkType.FUNCTION: [ChunkType.FUNCTION],
            ChunkType.METHOD: [ChunkType.METHOD],
        }
    
    def chunk(self, code: str, language: str) -> List[CodeChunk]:
        """Chunk code based on semantic relationships
        
        Args:
            code: The code to chunk
            language: The programming language
            
        Returns:
            List of code chunks
        """
        # First use basic strategy
        basic_chunks = super().chunk(code, language)
        
        # Analyze semantic relationships
        return self._group_related_chunks(basic_chunks)
    
    def _group_related_chunks(self, chunks: List[CodeChunk]) -> List[CodeChunk]:
        """Group related chunks together
        
        Args:
            chunks: List of code chunks
            
        Returns:
            Grouped code chunks
        """
        grouped = []
        current_group = []
        
        for chunk in chunks:
            if not current_group:
                current_group.append(chunk)
            else:
                # Check if should add to current group
                if self._should_group_together(current_group[-1], chunk):
                    current_group.append(chunk)
                else:
                    # End current group, start new group
                    grouped.extend(current_group)
                    current_group = [chunk]
        
        if current_group:
            grouped.extend(current_group)
        
        return grouped
    
    def _should_group_together(self, chunk1: CodeChunk, chunk2: CodeChunk) -> bool:
        """Determine if two chunks should be grouped together
        
        Args:
            chunk1: First code chunk
            chunk2: Second code chunk
            
        Returns:
            True if chunks should be grouped
        """
        # Adjacent lines
        if chunk2.start_line - chunk1.end_line <= 1:
            return True
        
        # Related types
        if chunk2.type in self.related_types.get(chunk1.type, []):
            return True
        
        # Name similarity
        if chunk1.name and chunk2.name:
            if chunk1.name in chunk2.name or chunk2.name in chunk1.name:
                return True
        
        return False 