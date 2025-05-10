"""
Incremental parsing support
"""

from typing import Dict, List, Tuple
from .models import CodeChunk, ParseResult

class IncrementalParser:
    """Incremental parser for efficient updates"""
    
    def __init__(self):
        self.cache: Dict[str, ParseResult] = {}
        self.file_hashes: Dict[str, str] = {}
    
    def parse_incremental(self, file_path: str, changes: List[Tuple[int, int, str]]) -> ParseResult:
        """Parse code incrementally based on changes
        
        Args:
            file_path: Path to the file
            changes: List of changes [(start_line, end_line, new_content), ...]
            
        Returns:
            Updated parse result
        """
        if file_path not in self.cache:
            # First parse, do full parse
            return self.full_parse(file_path)
        
        cached_result = self.cache[file_path]
        affected_chunks = self._find_affected_chunks(cached_result, changes)
        
        # Only reparse affected parts
        updated_chunks = self._reparse_chunks(affected_chunks, changes)
        
        # Merge results
        return self._merge_results(cached_result, updated_chunks)
    
    def _find_affected_chunks(self, result: ParseResult, changes: List[Tuple[int, int, str]]) -> List[CodeChunk]:
        """Find chunks affected by changes
        
        Args:
            result: Current parse result
            changes: List of changes
            
        Returns:
            List of affected chunks
        """
        affected = []
        
        for chunk in result.chunks:
            for start_line, end_line, _ in changes:
                if (chunk.start_line <= end_line and chunk.end_line >= start_line):
                    affected.append(chunk)
                    break
        
        return affected
    
    def _reparse_chunks(self, chunks: List[CodeChunk], changes: List[Tuple[int, int, str]]) -> List[CodeChunk]:
        """Reparse affected chunks with changes
        
        Args:
            chunks: List of chunks to reparse
            changes: List of changes
            
        Returns:
            List of updated chunks
        """
        # Implementation depends on specific language parser
        # This is a placeholder for the actual implementation
        return chunks
    
    def _merge_results(self, original: ParseResult, updated_chunks: List[CodeChunk]) -> ParseResult:
        """Merge original and updated results
        
        Args:
            original: Original parse result
            updated_chunks: List of updated chunks
            
        Returns:
            Merged parse result
        """
        # Implementation depends on specific language parser
        # This is a placeholder for the actual implementation
        return original 