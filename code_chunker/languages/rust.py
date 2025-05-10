"""Rust language processor"""

import re
from typing import List, Dict, Pattern

from .base import LanguageParser
from ..models import CodeChunk, Import, ChunkType


class RustParser(LanguageParser):
    """Rust language processor"""
    
    def _get_patterns(self) -> Dict[str, Pattern]:
        """Get language-specific regex patterns"""
        return {
            'function': re.compile(r'fn\s+(\w+)\s*\([^)]*\)\s*(->\s*[^\s{]+)?\s*{'),
            'struct': re.compile(r'struct\s+(\w+)\s*({|\()', re.MULTILINE),
            'enum': re.compile(r'enum\s+(\w+)\s*{', re.MULTILINE),
            'trait': re.compile(r'trait\s+(\w+)\s*{', re.MULTILINE),
            'impl': re.compile(r'impl\s+(?:<[^>]+>\s+)?(?:\w+\s+)?(\w+)\s*{', re.MULTILINE),
            'use': re.compile(
                r'use\s+(.+?);',
                re.MULTILINE
            ),
            'mod': re.compile(
                r'(?:pub\s+)?mod\s+(\w+)\s*(?:\{|;)',
                re.MULTILINE
            ),
        }
    
    def _find_matching_brace(self, code: str, start_pos: int) -> int:
        """Find the matching brace for a given position"""
        brace_count = 0
        pos = start_pos
        
        # Find the first left brace
        while pos < len(code) and code[pos] != '{':
            pos += 1
            
        if pos >= len(code):
            return start_pos  # No left brace found, return start position
            
        brace_count = 1  # Found the first left brace
        pos += 1  # Move to next character
        
        # Find matching right brace
        while pos < len(code) and brace_count > 0:
            if code[pos] == '{':
                brace_count += 1
            elif code[pos] == '}':
                brace_count -= 1
            pos += 1
            
            if pos >= len(code):
                return len(code) - 1  # Reached end of code, return last character position
                
        return pos - 1  # Return right brace position
    
    def extract_chunks(self, code: str) -> List[CodeChunk]:
        """Parse Rust code"""
        chunks = []
        
        # Extract functions
        for match in self._get_patterns()['function'].finditer(code):
            name = match.group(1)
            start_pos = match.start()
            end_pos = self._find_matching_brace(code, start_pos)
            
            if end_pos > start_pos:
                chunk_code = code[start_pos:end_pos + 1]
                chunks.append(CodeChunk(
                    type=ChunkType.FUNCTION,
                    name=name,
                    code=chunk_code,
                    start_line=code[:start_pos].count('\n') + 1,
                    end_line=code[:end_pos].count('\n') + 1,
                    language='rust',
                    confidence=0.9
                ))
        
        # Extract structs
        for match in self._get_patterns()['struct'].finditer(code):
            name = match.group(1)
            start_pos = match.start()
            # Determine if tuple struct or regular struct
            if match.group(2) == '(':  # Tuple struct, find semicolon
                end_pos = code.find(';', start_pos)
            else:  # Regular struct, find matching brace
                end_pos = self._find_matching_brace(code, start_pos)
            
            if end_pos > start_pos:
                chunk_code = code[start_pos:end_pos + 1]
                chunks.append(CodeChunk(
                    type=ChunkType.CLASS,
                    name=name,
                    code=chunk_code,
                    start_line=code[:start_pos].count('\n') + 1,
                    end_line=code[:end_pos].count('\n') + 1,
                    language='rust',
                    confidence=0.9
                ))
        
        # Extract enums
        for match in self._get_patterns()['enum'].finditer(code):
            name = match.group(1)
            start_pos = match.start()
            end_pos = self._find_matching_brace(code, start_pos)
            
            if end_pos > start_pos:
                chunk_code = code[start_pos:end_pos + 1]
                chunks.append(CodeChunk(
                    type=ChunkType.CLASS,
                    name=name,
                    code=chunk_code,
                    start_line=code[:start_pos].count('\n') + 1,
                    end_line=code[:end_pos].count('\n') + 1,
                    language='rust',
                    confidence=0.9
                ))
        
        # Extract traits
        for match in self._get_patterns()['trait'].finditer(code):
            name = match.group(1)
            start_pos = match.start()
            end_pos = self._find_matching_brace(code, start_pos)
            
            if end_pos > start_pos:
                chunk_code = code[start_pos:end_pos + 1]
                chunks.append(CodeChunk(
                    type=ChunkType.TRAIT,
                    name=name,
                    code=chunk_code,
                    start_line=code[:start_pos].count('\n') + 1,
                    end_line=code[:end_pos].count('\n') + 1,
                    language='rust',
                    confidence=0.9
                ))
        
        # Extract impl blocks
        for match in self._get_patterns()['impl'].finditer(code):
            name = match.group(1)
            start_pos = match.start()
            end_pos = self._find_matching_brace(code, start_pos)
            
            if end_pos > start_pos:
                chunk_code = code[start_pos:end_pos + 1]
                chunks.append(CodeChunk(
                    type=ChunkType.IMPL,
                    name=name,
                    code=chunk_code,
                    start_line=code[:start_pos].count('\n') + 1,
                    end_line=code[:end_pos].count('\n') + 1,
                    language='rust',
                    confidence=0.9
                ))
        
        return chunks
    
    def extract_imports(self, code: str) -> List[Import]:
        imports = []
        
        for match in self._get_patterns()['use'].finditer(code):
            import_path = match.group(1)
            line_number = code[:match.start()].count('\n')
            
            imports.append(Import(
                module=import_path,
                names=[],
                line_number=line_number
            ))
        
        return imports

    def parse(self, code: str) -> List[CodeChunk]:
        """Parse Rust code"""
        return self.extract_chunks(code)
