"""
Go language processor
"""

import re
from typing import List, Dict, Pattern

from .base import LanguageProcessor
from ..models import CodeChunk, Import, ChunkType


class GoProcessor(LanguageProcessor):
    """Go語言處理器"""
    
    def _get_patterns(self) -> Dict[str, Pattern]:
        return {
            'function': re.compile(
                r'func\s+(?:\(\s*\w+\s+[^)]+\)\s+)?(\w+)\s*\([^)]*\)(?:\s+[^{]+)?\s*\{',
                re.MULTILINE
            ),
            'struct': re.compile(
                r'type\s+(\w+)\s+struct\s*\{',
                re.MULTILINE
            ),
            'interface': re.compile(
                r'type\s+(\w+)\s+interface\s*\{',
                re.MULTILINE
            ),
            'method': re.compile(
                r'func\s+\(\s*\w+\s+([^)]+)\)\s+(\w+)\s*\([^)]*\)(?:\s+[^{]+)?\s*\{',
                re.MULTILINE
            ),
            'import': re.compile(
                r'import\s+(?:"([^"]+)"|\(\s*([^)]+)\s*\))',
                re.MULTILINE | re.DOTALL
            ),
            'type_alias': re.compile(
                r'type\s+(\w+)\s+(?:=\s+)?(\w+)',
                re.MULTILINE
            ),
        }
    
    def extract_chunks(self, code: str) -> List[CodeChunk]:
        chunks = []
        
        # 提取函數
        for match in self.patterns['function'].finditer(code):
            name = match.group(1)
            start_pos = match.start()
            start_line = code[:start_pos].count('\n')
            
            end_pos = self._find_matching_brace(code, match.end() - 1)
            end_line = code[:end_pos].count('\n')
            
            function_code = code[start_pos:end_pos + 1]
            
            chunks.append(CodeChunk(
                type=ChunkType.FUNCTION,
                name=name,
                code=function_code,
                start_line=start_line,
                end_line=end_line,
                language='go',
                confidence=0.95
            ))
        
        # 提取方法
        for match in self.patterns['method'].finditer(code):
            receiver = match.group(1)
            name = match.group(2)
            start_pos = match.start()
            start_line = code[:start_pos].count('\n')
            
            end_pos = self._find_matching_brace(code, match.end() - 1)
            end_line = code[:end_pos].count('\n')
            
            method_code = code[start_pos:end_pos + 1]
            
            chunks.append(CodeChunk(
                type=ChunkType.METHOD,
                name=name,
                code=method_code,
                start_line=start_line,
                end_line=end_line,
                language='go',
                confidence=0.95,
                metadata={'receiver': receiver}
            ))
        
        # 提取結構體
        for match in self.patterns['struct'].finditer(code):
            name = match.group(1)
            start_pos = match.start()
            start_line = code[:start_pos].count('\n')
            
            end_pos = self._find_matching_brace(code, match.end() - 1)
            end_line = code[:end_pos].count('\n')
            
            struct_code = code[start_pos:end_pos + 1]
            
            chunks.append(CodeChunk(
                type=ChunkType.CLASS,
                name=name,
                code=struct_code,
                start_line=start_line,
                end_line=end_line,
                language='go',
                confidence=0.95,
                metadata={'go_type': 'struct'}
            ))
        
        # 提取介面
        for match in self.patterns['interface'].finditer(code):
            name = match.group(1)
            start_pos = match.start()
            start_line = code[:start_pos].count('\n')
            
            end_pos = self._find_matching_brace(code, match.end() - 1)
            end_line = code[:end_pos].count('\n')
            
            interface_code = code[start_pos:end_pos + 1]
            
            chunks.append(CodeChunk(
                type=ChunkType.CLASS,
                name=name,
                code=interface_code,
                start_line=start_line,
                end_line=end_line,
                language='go',
                confidence=0.95,
                metadata={'go_type': 'interface'}
            ))
        
        return chunks
    
    def extract_imports(self, code: str) -> List[Import]:
        imports = []
        
        for match in self.patterns['import'].finditer(code):
            single_import = match.group(1)
            multi_imports = match.group(2)
            line_number = code[:match.start()].count('\n')
            
            if single_import:
                imports.append(Import(
                    module=single_import,
                    names=[],
                    line_number=line_number
                ))
            elif multi_imports:
                # 處理多行import
                for line in multi_imports.strip().split('\n'):
                    line = line.strip()
                    if line and line.startswith('"') and line.endswith('"'):
                        imports.append(Import(
                            module=line.strip('"'),
                            names=[],
                            line_number=line_number
                        ))
        
        return imports
