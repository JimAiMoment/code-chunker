"""Python language processor"""

import re
from typing import Dict, List, Pattern

from .base import LanguageParser
from ..models import CodeChunk, ChunkType

class PythonParser(LanguageParser):
    """Python language parser"""
    
    def _get_patterns(self):
        return {
            'function': re.compile(r'def\s+(\w+)\s*\([^)]*\)\s*:'),
            'class': re.compile(r'class\s+(\w+)\s*(?:\([^)]*\))?\s*:'),
            'import': re.compile(r'import\s+\w+|from\s+\w+\s+import\s+\w+'),
        }
    
    def find_block_end(self, code: str, start_line: int, indent_level: int) -> int:
        """Find the end of a Python code block"""
        lines = code.split('\n')
        current_line = start_line + 1
        
        while current_line < len(lines):
            line = lines[current_line]
            if not line.strip():  # 跳过空行
                current_line += 1
                continue
                
            current_indent = len(line) - len(line.lstrip())
            if current_indent <= indent_level:
                return current_line
            current_line += 1
            
        return len(lines)
    
    def parse(self, code: str) -> List[CodeChunk]:
        """Parse Python code"""
        chunks = []
        
        # Extract functions
        for match in self._get_patterns()['function'].finditer(code):
            name = match.group(1)
            start_pos = match.start()
            start_line = code[:start_pos].count('\n')
            indent_level = self._get_indent(code, start_pos)
            end_line = self.find_block_end(code, start_line, indent_level)
            
            if end_line > start_line:
                chunk_code = '\n'.join(code.split('\n')[start_line:end_line])
                chunks.append(CodeChunk(
                    type=ChunkType.FUNCTION,
                    name=name,
                    code=chunk_code,
                    start_line=start_line + 1,
                    end_line=end_line,
                    language='python',
                    confidence=0.9
                ))
        
        # Extract classes
        for match in self._get_patterns()['class'].finditer(code):
            name = match.group(1)
            start_pos = match.start()
            start_line = code[:start_pos].count('\n')
            indent_level = self._get_indent(code, start_pos)
            end_line = self.find_block_end(code, start_line, indent_level)
            
            if end_line > start_line:
                chunk_code = '\n'.join(code.split('\n')[start_line:end_line])
                chunks.append(CodeChunk(
                    type=ChunkType.CLASS,
                    name=name,
                    code=chunk_code,
                    start_line=start_line + 1,
                    end_line=end_line,
                    language='python',
                    confidence=0.9
                ))
        
        return chunks
    
    def extract_imports(self, code: str) -> List[str]:
        """Extract import statements"""
        imports = []
        for match in self._get_patterns()['import'].finditer(code):
            imports.append(match.group(0))
        return imports
    
    def _get_indent(self, code: str, pos: int) -> int:
        """Get indentation level at position"""
        line = code[:pos].split('\n')[-1]
        return len(line) - len(line.lstrip())

    def extract_chunks(self, code: str) -> List[CodeChunk]:
        return self.parse(code)
