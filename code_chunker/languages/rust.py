"""Rust language processor"""

import re
from typing import List, Dict, Pattern

from .base import LanguageParser
from ..models import CodeChunk, Import, ChunkType


class RustParser(LanguageParser):
    """Rust language processor"""
    
    @property
    def patterns(self) -> Dict[str, Pattern]:
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
    
    def extract_chunks(self, code: str) -> List[CodeChunk]:
        """Parse Rust code"""
        chunks = []
        
        # Extract functions
        for match in self.patterns['function'].finditer(code):
            name = match.group(1)
            start_pos = match.start()
            end_pos = self.find_matching_brace(code, start_pos)
            
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
        for match in self.patterns['struct'].finditer(code):
            name = match.group(1)
            start_pos = match.start()
            # Determine if tuple struct or regular struct
            if match.group(2) == '(':  # Tuple struct, find semicolon
                end_pos = code.find(';', start_pos)
            else:  # Regular struct, find matching brace
                end_pos = self.find_matching_brace(code, start_pos)
            
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
        for match in self.patterns['enum'].finditer(code):
            name = match.group(1)
            start_pos = match.start()
            end_pos = self.find_matching_brace(code, start_pos)
            
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
        for match in self.patterns['trait'].finditer(code):
            name = match.group(1)
            start_pos = match.start()
            end_pos = self.find_matching_brace(code, start_pos)
            
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
        for match in self.patterns['impl'].finditer(code):
            name = match.group(1)
            start_pos = match.start()
            end_pos = self.find_matching_brace(code, start_pos)
            
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
        
        for match in self.patterns['use'].finditer(code):
            import_path = match.group(1)
            line_number = code[:match.start()].count('\n')
            
            imports.append(Import(
                module=import_path,
                names=[],
                line_number=line_number
            ))
        
        return imports
