"""
Rust language processor
"""

import re
from typing import List, Dict, Pattern

from .base import LanguageProcessor
from ..models import CodeChunk, Import, ChunkType


class RustProcessor(LanguageProcessor):
    """Rust語言處理器"""
    
    def _get_patterns(self) -> Dict[str, Pattern]:
        return {
            'function': re.compile(
                r'(?:pub\s+)?(?:async\s+)?fn\s+(\w+)\s*(?:<[^>]+>)?\s*\([^)]*\)(?:\s*->\s*[^{]+)?\s*\{',
                re.MULTILINE
            ),
            'struct': re.compile(
                r'(?:pub\s+)?struct\s+(\w+)(?:<[^>]+>)?\s*(?:\{|\()',
                re.MULTILINE
            ),
            'enum': re.compile(
                r'(?:pub\s+)?enum\s+(\w+)(?:<[^>]+>)?\s*\{',
                re.MULTILINE
            ),
            'trait': re.compile(
                r'(?:pub\s+)?trait\s+(\w+)(?:<[^>]+>)?\s*\{',
                re.MULTILINE
            ),
            'impl': re.compile(
                r'impl(?:<[^>]+>)?\s+(?:(\w+)\s+for\s+)?(\w+)(?:<[^>]+>)?\s*\{',
                re.MULTILINE
            ),
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
                language='rust',
                confidence=0.95
            ))
        
        # 提取結構體
        for match in self.patterns['struct'].finditer(code):
            name = match.group(1)
            start_pos = match.start()
            start_line = code[:start_pos].count('\n')
            
            # 判斷是 tuple struct 還是普通 struct
            if code[match.end() - 1] == '(':
                # Tuple struct，找到分號
                end_pos = code.find(';', match.end())
                if end_pos == -1:
                    end_pos = code.find('\n', match.end())
            else:
                # 普通struct，找到匹配的大括號
                end_pos = self._find_matching_brace(code, match.end() - 1)
            
            end_line = code[:end_pos].count('\n')
            struct_code = code[start_pos:end_pos + 1]
            
            chunks.append(CodeChunk(
                type=ChunkType.CLASS,
                name=name,
                code=struct_code,
                start_line=start_line,
                end_line=end_line,
                language='rust',
                confidence=0.95,
                metadata={'rust_type': 'struct'}
            ))
        
        # 提取枚舉
        for match in self.patterns['enum'].finditer(code):
            name = match.group(1)
            start_pos = match.start()
            start_line = code[:start_pos].count('\n')
            
            end_pos = self._find_matching_brace(code, match.end() - 1)
            end_line = code[:end_pos].count('\n')
            
            enum_code = code[start_pos:end_pos + 1]
            
            chunks.append(CodeChunk(
                type=ChunkType.CLASS,
                name=name,
                code=enum_code,
                start_line=start_line,
                end_line=end_line,
                language='rust',
                confidence=0.95,
                metadata={'rust_type': 'enum'}
            ))
        
        # 提取trait
        for match in self.patterns['trait'].finditer(code):
            name = match.group(1)
            start_pos = match.start()
            start_line = code[:start_pos].count('\n')
            
            end_pos = self._find_matching_brace(code, match.end() - 1)
            end_line = code[:end_pos].count('\n')
            
            trait_code = code[start_pos:end_pos + 1]
            
            chunks.append(CodeChunk(
                type=ChunkType.CLASS,
                name=name,
                code=trait_code,
                start_line=start_line,
                end_line=end_line,
                language='rust',
                confidence=0.95,
                metadata={'rust_type': 'trait'}
            ))
        
        # 提取impl塊
        for match in self.patterns['impl'].finditer(code):
            trait_name = match.group(1)
            type_name = match.group(2)
            start_pos = match.start()
            start_line = code[:start_pos].count('\n')
            
            end_pos = self._find_matching_brace(code, match.end() - 1)
            end_line = code[:end_pos].count('\n')
            
            impl_code = code[start_pos:end_pos + 1]
            
            name = f"{trait_name} for {type_name}" if trait_name else type_name
            
            chunks.append(CodeChunk(
                type=ChunkType.CLASS,
                name=name,
                code=impl_code,
                start_line=start_line,
                end_line=end_line,
                language='rust',
                confidence=0.9,
                metadata={'rust_type': 'impl', 'trait': trait_name, 'for_type': type_name}
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
