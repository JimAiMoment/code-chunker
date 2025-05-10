"""
Python language processor
"""

import re
from typing import List, Dict, Pattern

from .base import LanguageProcessor
from ..models import CodeChunk, Import, ChunkType


class PythonProcessor(LanguageProcessor):
    """Python語言處理器"""
    
    def _get_patterns(self) -> Dict[str, Pattern]:
        return {
            'function': re.compile(r'^(\s*)(?:async\s+)?def\s+(\w+)\s*\([^)]*\).*?:', re.MULTILINE),
            'class': re.compile(r'^(\s*)class\s+(\w+)\s*(?:\([^)]*\))?\s*:', re.MULTILINE),
            'method': re.compile(r'^(\s{4,})(?:async\s+)?def\s+(\w+)\s*\([^)]*\).*?:', re.MULTILINE),
            'import': re.compile(r'^(?:from\s+([\w.]+)\s+)?import\s+([^#\n]+)', re.MULTILINE),
            'decorator': re.compile(r'^(\s*)@(\w+(?:\.\w+)*)\s*(?:\([^)]*\))?', re.MULTILINE),
        }
    
    def extract_chunks(self, code: str) -> List[CodeChunk]:
        chunks = []
        lines = code.split('\n')
        
        # 提取函數
        for match in self.patterns['function'].finditer(code):
            indent = match.group(1)
            name = match.group(2)
            start_line = code[:match.start()].count('\n')
            
            # 找到函數結束
            indent_level = len(indent)
            end_line = self._find_block_end(lines, start_line, indent_level)
            
            # 獲取完整函數代碼
            function_code = '\n'.join(lines[start_line:end_line + 1])
            
            # 檢查是否為方法
            chunk_type = ChunkType.METHOD if indent_level > 0 else ChunkType.FUNCTION
            
            chunks.append(CodeChunk(
                type=chunk_type,
                name=name,
                code=function_code,
                start_line=start_line,
                end_line=end_line,
                language='python',
                confidence=0.95,
                metadata={'indent_level': indent_level}
            ))
        
        # 提取類
        for match in self.patterns['class'].finditer(code):
            indent = match.group(1)
            name = match.group(2)
            start_line = code[:match.start()].count('\n')
            
            # 找到類結束
            indent_level = len(indent)
            end_line = self._find_block_end(lines, start_line, indent_level)
            
            class_code = '\n'.join(lines[start_line:end_line + 1])
            
            chunks.append(CodeChunk(
                type=ChunkType.CLASS,
                name=name,
                code=class_code,
                start_line=start_line,
                end_line=end_line,
                language='python',
                confidence=0.95,
                metadata={'indent_level': indent_level}
            ))
        
        return chunks
    
    def extract_imports(self, code: str) -> List[Import]:
        imports = []
        
        for match in self.patterns['import'].finditer(code):
            from_module = match.group(1)
            import_names = match.group(2)
            line_number = code[:match.start()].count('\n')
            
            # 解析導入的名稱
            names = []
            for name in import_names.split(','):
                name = name.strip()
                if ' as ' in name:
                    original, alias = name.split(' as ')
                    names.append(original.strip())
                else:
                    names.append(name)
            
            imports.append(Import(
                module=from_module or '',
                names=names,
                line_number=line_number
            ))
        
        return imports
