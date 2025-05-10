"""
Incremental parsing support
"""

import os
import hashlib
from typing import Dict, List, Tuple, Set, Optional, Any
from pathlib import Path

from .models import CodeChunk, ParseResult, ChunkType, Import
from .chunker import CodeChunker


class IncrementalParser:
    """Incremental parser for efficient updates"""
    
    def __init__(self, chunker: Optional[CodeChunker] = None):
        self.cache: Dict[str, ParseResult] = {}
        self.file_hashes: Dict[str, str] = {}
        self.chunker = chunker or CodeChunker()
    
    def full_parse(self, file_path: str) -> ParseResult:
        """Perform a full parse of the file and cache the result
        
        Args:
            file_path: Path to the file
            
        Returns:
            Parse result
        """
        result = self.chunker.parse_file(file_path)
        
        # Cache the result
        self.cache[file_path] = result
        
        # Store file hash
        self.file_hashes[file_path] = self._compute_file_hash(file_path)
        
        return result
    
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
        
        # Apply changes to the raw code
        updated_code = self._apply_changes(cached_result.raw_code, changes)
        
        # Write the updated code to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_code)
        
        # Find affected chunks
        affected_chunks = self._find_affected_chunks(cached_result, changes)
        
        # Only reparse affected parts
        updated_chunks = self._reparse_chunks(affected_chunks, changes, updated_code, cached_result.language, file_path)
        
        # Merge results
        result = self._merge_results(cached_result, updated_chunks, updated_code)
        
        # Update cache
        self.cache[file_path] = result
        self.file_hashes[file_path] = self._compute_file_hash(file_path)
        
        return result
    
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
    
    def _reparse_chunks(self, chunks: List[CodeChunk], changes: List[Tuple[int, int, str]], 
                        updated_code: str, language: str, file_path: str) -> List[CodeChunk]:
        """Reparse affected chunks with changes
        
        Args:
            chunks: List of chunks to reparse
            changes: List of changes
            updated_code: The updated code after applying changes
            language: The programming language
            file_path: Path to the file
            
        Returns:
            List of updated chunks
        """
        # If there are no affected chunks or changes, return an empty list
        if not chunks and not changes:
            return []
        
        # Calculate line number offsets after changes
        line_offsets = self._calculate_line_offsets(changes)
        
        # Find the range of affected lines
        affected_lines = set()
        for start_line, end_line, new_content in changes:
            # Add affected lines
            for line in range(start_line, end_line + 1):
                affected_lines.add(line)
        
        # Adjust line numbers for unaffected chunks
        adjusted_chunks = []
        for chunk in chunks:
            # Deep copy chunk to avoid modifying original data
            adjusted_chunk = CodeChunk(
                type=chunk.type,
                name=chunk.name,
                code=chunk.code,
                start_line=chunk.start_line,
                end_line=chunk.end_line,
                language=chunk.language,
                confidence=chunk.confidence,
                metadata=chunk.metadata.copy() if chunk.metadata else {}
            )
            
            # Apply line number offsets
            for start_line, end_line, new_content in changes:
                new_lines_count = new_content.count('\n') + 1 if new_content else 0
                line_diff = new_lines_count - (end_line - start_line)
                
                # If chunk is affected, adjust its line numbers
                if adjusted_chunk.start_line > end_line:
                    adjusted_chunk.start_line += line_diff
                    adjusted_chunk.end_line += line_diff
                # If chunk spans change area, adjust its end line number
                elif adjusted_chunk.start_line <= start_line and adjusted_chunk.end_line >= end_line:
                    adjusted_chunk.end_line += line_diff
            
            # Check if chunk is affected
            is_affected = False
            for line in affected_lines:
                if adjusted_chunk.start_line <= line <= adjusted_chunk.end_line:
                    is_affected = True
                    break
            
            if not is_affected:
                adjusted_chunks.append(adjusted_chunk)
        
        # If more than 50% of code chunks are affected, reparse entire file
        if len(chunks) - len(adjusted_chunks) > len(chunks) * 0.5:
            result = self.chunker.parse(updated_code, language)
            result.file_path = file_path
            return result.chunks
        
        # Reparse entire file, but only keep new or modified chunks
        new_result = self.chunker.parse(updated_code, language)
        new_result.file_path = file_path
        
        # Merge new parsed chunks with unaffected chunks
        merged_chunks = list(adjusted_chunks)  # Copy unaffected chunks list
        
        # Check if new parsed chunks are new or modified
        for new_chunk in new_result.chunks:
            # Check if new chunk
            is_new = True
            for old_chunk in adjusted_chunks:
                # If name, type, and location are similar, consider them same chunk
                if (old_chunk.name == new_chunk.name and 
                    old_chunk.type == new_chunk.type and 
                    abs(old_chunk.start_line - new_chunk.start_line) <= 3):  # Allow small range of line number changes
                    is_new = False
                    break
            
            if is_new:
                # Check if in affected area
                is_in_affected_area = False
                for line in affected_lines:
                    if new_chunk.start_line <= line <= new_chunk.end_line:
                        is_in_affected_area = True
                        break
                
                # If new chunk or in affected area, add to result
                if is_in_affected_area:
                    merged_chunks.append(new_chunk)
        
        # Sort by start line
        merged_chunks.sort(key=lambda x: x.start_line)
        
        # Remove duplicate chunks
        unique_chunks = []
        seen_signatures = set()
        
        for chunk in merged_chunks:
            # Create unique signature for chunk
            signature = (chunk.name, chunk.type, chunk.start_line)
            if signature not in seen_signatures:
                seen_signatures.add(signature)
                unique_chunks.append(chunk)
        
        return unique_chunks
    
    def _calculate_line_offsets(self, changes: List[Tuple[int, int, str]]) -> Dict[int, int]:
        """Calculate line number offsets
        
        Args:
            changes: Change list
            
        Returns:
            Line number offset dictionary
        """
        offsets = {}
        
        # Sort changes by start line
        sorted_changes = sorted(changes, key=lambda x: x[0])
        
        current_offset = 0
        for start_line, end_line, new_content in sorted_changes:
            # Calculate new content line count
            new_lines_count = new_content.count('\n') + 1 if new_content else 0
            # Calculate original content line count
            original_lines_count = end_line - start_line + 1
            # Calculate line count difference
            line_diff = new_lines_count - original_lines_count
            
            # Update current offset
            current_offset += line_diff
            
            # Record line number offset after this change
            offsets[end_line] = current_offset
        
        return offsets
    
    def _merge_results(self, original: ParseResult, updated_chunks: List[CodeChunk], 
                       updated_code: str) -> ParseResult:
        """Merge original and updated results
        
        Args:
            original: Original parse result
            updated_chunks: List of updated chunks
            updated_code: The updated code after applying changes
            
        Returns:
            Merged parse result
        """
        # Update imports and exports
        updated_imports = self._update_imports(original.imports, updated_chunks, updated_code)
        updated_exports = self._update_exports(original.exports, updated_chunks, updated_code)
        
        # Create new metadata, retain original metadata information
        metadata = original.metadata.copy() if original.metadata else {}
        metadata.update({
            'incremental_update': True,
            'original_chunk_count': len(original.chunks),
            'updated_chunk_count': len(updated_chunks),
            'timestamp': Path(original.file_path).stat().st_mtime if original.file_path else None
        })
        
        return ParseResult(
            language=original.language,
            file_path=original.file_path,
            chunks=updated_chunks,
            imports=updated_imports,
            exports=updated_exports,
            raw_code=updated_code,
            metadata=metadata
        )
    
    def _apply_changes(self, code: str, changes: List[Tuple[int, int, str]]) -> str:
        """Apply changes to code
        
        Args:
            code: Original code
            changes: List of changes [(start_line, end_line, new_content), ...]
            
        Returns:
            Updated code
        """
        lines = code.split('\n')
        
        # Sort changes in reverse order to avoid line number shifts
        sorted_changes = sorted(changes, key=lambda x: x[0], reverse=True)
        
        for start_line, end_line, new_content in sorted_changes:
            # Adjust for 0-based indexing
            start_idx = start_line - 1
            end_idx = end_line
            
            # Replace the affected lines
            lines[start_idx:end_idx] = new_content.split('\n') if new_content else []
        
        return '\n'.join(lines)
    
    def _update_imports(self, original_imports: List[Import], updated_chunks: List[CodeChunk], 
                       updated_code: str) -> List[Import]:
        """Update imports based on updated chunks
        
        Args:
            original_imports: Original imports
            updated_chunks: Updated chunks
            updated_code: Updated code content
            
        Returns:
            Updated imports
        """
        # Check if any import chunks are modified
        import_chunks = [c for c in updated_chunks if c.type == ChunkType.IMPORT]
        
        if not import_chunks and not any(c.code and 'import' in c.code for c in updated_chunks):
            # If no import chunks are modified, retain original imports
            return original_imports
        
        # Reparse imports using language-specific parser
        language = updated_chunks[0].language if updated_chunks else None
        if not language:
            return original_imports
        
        # Use chunker to reparse updated code and extract imports
        result = self.chunker.parse(updated_code, language)
        updated_imports = result.imports
        
        # If no imports found, retain original imports
        if not updated_imports:
            return original_imports
        
        return updated_imports
    
    def _update_exports(self, original_exports: List[str], updated_chunks: List[CodeChunk], 
                       updated_code: str) -> List[str]:
        """Update exports based on updated chunks
        
        Args:
            original_exports: Original exports
            updated_chunks: Updated chunks
            updated_code: Updated code content
            
        Returns:
            Updated exports
        """
        # Check if any export chunks are modified
        export_chunks = [c for c in updated_chunks if c.type == ChunkType.EXPORT]
        
        if not export_chunks and not any(c.code and 'export' in c.code for c in updated_chunks):
            # If no export chunks are modified, retain original exports
            return original_exports
        
        # Reparse exports using language-specific parser
        language = updated_chunks[0].language if updated_chunks else None
        if not language:
            return original_exports
        
        # Use chunker to reparse updated code and extract exports
        result = self.chunker.parse(updated_code, language)
        updated_exports = result.exports
        
        # If no exports found, retain original exports
        if not updated_exports:
            return original_exports
        
        return updated_exports
    
    def _compute_file_hash(self, file_path: str) -> str:
        """Compute hash of file content
        
        Args:
            file_path: Path to the file
            
        Returns:
            Hash of file content
        """
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def invalidate_cache(self, file_path: Optional[str] = None) -> None:
        """Invalidate cache for a file or all files
        
        Args:
            file_path: Path to the file, or None to invalidate all
        """
        if file_path is None:
            self.cache.clear()
            self.file_hashes.clear()
        else:
            if file_path in self.cache:
                del self.cache[file_path]
            if file_path in self.file_hashes:
                del self.file_hashes[file_path] 