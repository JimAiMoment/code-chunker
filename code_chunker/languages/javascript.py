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
            'import': re.compile(r'import\s+(?:(.+?)\s+from\s+|(\{[^}]*\})\s+from\s+)?[\'"](.*?)[\'"]'),
            'export': re.compile(r'export\s+(?:default\s+)?(?:class|function|const|let|var)\s+(\w+)'),
        }
    
    def parse(self, code: str) -> List[CodeChunk]:
        """Parse JavaScript code and extract chunks"""
        return self.extract_chunks(code)
    
    def extract_chunks(self, code: str) -> List[CodeChunk]:
        """Parse JavaScript code"""
        chunks = []
        
        # Extract functions
        for match in self._get_patterns()['function'].finditer(code):
            name = match.group(1)
            start_pos = match.start()
            start_line = code[:start_pos].count('\n')
            
            # Find function end (matching braces)
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
            
            # Find arrow function end
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
            
            # Find class end
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
        
        # Regular expressions matching different types of imports
        import_patterns = [
            # Default import: import React from 'react'
            re.compile(r'import\s+(\w+)\s+from\s+[\'"]([^\'"]*)[\'"]\s*;?'),
            
            # Named import: import { useState, useEffect } from 'react'
            re.compile(r'import\s+\{([^}]*)\}\s+from\s+[\'"]([^\'"]*)[\'"]\s*;?'),
            
            # Namespace import: import * as utils from './utils'
            re.compile(r'import\s+\*\s+as\s+(\w+)\s+from\s+[\'"]([^\'"]*)[\'"]\s*;?'),
            
            # Simple import: import './styles.css'
            re.compile(r'import\s+[\'"]([^\'"]*)[\'"]'),
        ]
        
        # Process each import pattern
        for pattern in import_patterns:
            for match in pattern.finditer(code):
                if pattern == import_patterns[0]:  # Default import
                    name = match.group(1)
                    module = match.group(2)
                    imports.append(Import(
                        module=module,
                        names=[name],
                        line_number=code[:match.start()].count('\n')
                    ))
                elif pattern == import_patterns[1]:  # Named import
                    names_str = match.group(1)
                    module = match.group(2)
                    # Process named import aliases
                    names = []
                    for name in names_str.split(','):
                        name = name.strip()
                        if ' as ' in name:
                            name = name.split(' as ')[0].strip()
                        if name:
                            names.append(name)
                    
                    imports.append(Import(
                        module=module,
                        names=names,
                        line_number=code[:match.start()].count('\n')
                    ))
                elif pattern == import_patterns[2]:  # Namespace import
                    name = match.group(1)
                    module = match.group(2)
                    imports.append(Import(
                        module=module,
                        names=[name],
                        line_number=code[:match.start()].count('\n'),
                        alias='*'
                    ))
                else:  # Simple import
                    module = match.group(1)
                    # Special handling for CSS files
                    name = 'css' if module.endswith('.css') else 'module'
                    imports.append(Import(
                        module=module,
                        names=[name],
                        line_number=code[:match.start()].count('\n')
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
                # Check if it's a single-line arrow function
                next_line_start = pos + 1
                if next_line_start < len(code):
                    next_line = code[next_line_start:].split('\n')[0]
                    if next_line.strip() and not next_line.strip().startswith('.'):
                        return pos
            pos += 1
        
        return len(code)
