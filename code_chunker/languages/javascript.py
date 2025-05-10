"""JavaScript language processor"""

import re
from typing import List, Dict, Pattern

from .base import LanguageParser
from ..models import CodeChunk, Import, ChunkType


class JavaScriptParser(LanguageParser):
    """JavaScript language parser"""
    
    def _get_patterns(self):
        return {
            'function': re.compile(r'function\s+(\w+)\s*\([^)]*\)\s*{'),
            'arrow_function': re.compile(r'(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>'),
            'class': re.compile(r'class\s+(\w+)(?:\s+extends\s+\w+)?\s*{'),
            'import': re.compile(r'import\s+(?:\{[^}]*\}|\w+)\s+from\s+[\'"][^\'"]+[\'"]'),
            'export': re.compile(r'export\s+(?:default\s+)?(?:class|function|const|let|var)'),
        }
    
    def extract_chunks(self, code: str) -> List[CodeChunk]:
        """Parse JavaScript code"""
        chunks = []
        
        # Extract functions
        for match in self._get_patterns()['function'].finditer(code):
            name = match.group(1)
            start_pos = match.start()
            start_line = code[:start_pos].count('\n')
            
            # 找到函數結束（匹配大括號）
            end_pos = self._find_matching_brace(code, match.end() - 1)
            end_line = code[:end_pos].count('\n')
            
            function_code = code[start_pos:end_pos + 1]
            
            chunks.append(CodeChunk(
                type=ChunkType.FUNCTION,
                name=name,
                code=function_code,
                start_line=start_line,
                end_line=end_line,
                language='javascript',
                confidence=0.95
            ))
        
        # Extract arrow functions
        for match in self._get_patterns()['arrow_function'].finditer(code):
            name = match.group(1)
            start_pos = match.start()
            start_line = code[:start_pos].count('\n')
            
            # 找到箭頭函數結束
            end_pos = self._find_arrow_function_end(code, match.end())
            end_line = code[:end_pos].count('\n')
            
            function_code = code[start_pos:end_pos]
            
            chunks.append(CodeChunk(
                type=ChunkType.FUNCTION,
                name=name,
                code=function_code,
                start_line=start_line,
                end_line=end_line,
                language='javascript',
                confidence=0.9,
                metadata={'is_arrow': True}
            ))
        
        # Extract classes
        for match in self._get_patterns()['class'].finditer(code):
            name = match.group(1)
            start_pos = match.start()
            start_line = code[:start_pos].count('\n')
            
            # 找到類結束
            end_pos = self._find_matching_brace(code, match.end() - 1)
            end_line = code[:end_pos].count('\n')
            
            class_code = code[start_pos:end_pos + 1]
            
            chunks.append(CodeChunk(
                type=ChunkType.CLASS,
                name=name,
                code=class_code,
                start_line=start_line,
                end_line=end_line,
                language='javascript',
                confidence=0.95
            ))
        
        return chunks
    
    def extract_imports(self, code: str) -> List[Import]:
        """Extract import statements"""
        imports = []
        
        for match in self._get_patterns()['import'].finditer(code):
            default_import = match.group(1)
            named_imports = match.group(2)
            module = match.group(3)
            line_number = code[:match.start()].count('\n')
            
            names = []
            if default_import:
                names.append(default_import.strip())
            if named_imports:
                names.extend([
                    name.strip() 
                    for name in named_imports.split(',')
                ])
            
            imports.append(Import(
                module=module,
                names=names,
                line_number=line_number
            ))
        
        return imports
    
    def extract_exports(self, code: str) -> List[str]:
        """Extract export statements"""
        exports = []
        
        for match in self._get_patterns()['export'].finditer(code):
            name = match.group(1)
            if name:
                exports.append(name)
        
        return exports
    
    def _find_arrow_function_end(self, code: str, start_pos: int) -> int:
        """Find arrow function end position"""
        # Simplified: look for semicolon or newline
        pos = start_pos
        in_braces = 0
        
        while pos < len(code):
            if code[pos] == '{':
                in_braces += 1
            elif code[pos] == '}':
                in_braces -= 1
                if in_braces == 0:
                    return pos + 1
            elif code[pos] == ';' and in_braces == 0:
                return pos + 1
            elif code[pos] == '\n' and in_braces == 0:
                # 檢查是否為單行箭頭函數
                next_line_start = pos + 1
                if next_line_start < len(code):
                    next_line = code[next_line_start:].split('\n')[0]
                    if next_line.strip() and not next_line.strip().startswith('.'):
                        return pos
            pos += 1
        
        return len(code)
