"""
TypeScript language processor
"""

from typing import Dict, Pattern, List
import re

from .javascript import JavaScriptParser
from ..models import CodeChunk, ChunkType


class TypeScriptParser(JavaScriptParser):
    """TypeScript語言處理器（繼承自JavaScript）"""
    
    def _get_patterns(self) -> Dict[str, Pattern]:
        patterns = super()._get_patterns()
        
        # 添加TypeScript特定的模式
        patterns.update({
            'interface': re.compile(
                r'interface\s+(\w+)(?:\s+extends\s+[^{]+)?\s*\{',
                re.MULTILINE
            ),
            'type_alias': re.compile(
                r'type\s+(\w+)\s*=\s*[^;]+;',
                re.MULTILINE
            ),
            'enum': re.compile(
                r'enum\s+(\w+)\s*\{',
                re.MULTILINE
            ),
            'generic_function': re.compile(
                r'(?:async\s+)?function\s+(\w+)\s*<[^>]+>\s*\([^)]*\)\s*(?::\s*[^{]+)?\s*\{',
                re.MULTILINE
            ),
        })
        
        return patterns
    
    def extract_chunks(self, code: str) -> List[CodeChunk]:
        # 獲取JavaScript的chunks
        chunks = super().extract_chunks(code)
        
        # 添加TypeScript特定的chunks
        
        # 提取介面
        for match in self.patterns['interface'].finditer(code):
            name = match.group(1)
            start_pos = match.start()
            start_line = code[:start_pos].count('\n')
            
            end_pos = self._find_matching_brace(code, match.end() - 1)
            end_line = code[:end_pos].count('\n')
            
            interface_code = code[start_pos:end_pos + 1]
            
            chunks.append(CodeChunk(
                type=ChunkType.CLASS,  # 將interface視為class類型
                name=name,
                code=interface_code,
                start_line=start_line,
                end_line=end_line,
                language='typescript',
                confidence=0.95,
                metadata={'is_interface': True}
            ))
        
        # 提取類型別名
        for match in self.patterns['type_alias'].finditer(code):
            name = match.group(1)
            start_pos = match.start()
            start_line = code[:start_pos].count('\n')
            end_line = start_line  # 類型別名通常是單行
            
            type_code = match.group(0)
            
            chunks.append(CodeChunk(
                type=ChunkType.VARIABLE,  # 將type alias視為variable
                name=name,
                code=type_code,
                start_line=start_line,
                end_line=end_line,
                language='typescript',
                confidence=0.9,
                metadata={'is_type_alias': True}
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
                type=ChunkType.CLASS,  # 將enum視為class類型
                name=name,
                code=enum_code,
                start_line=start_line,
                end_line=end_line,
                language='typescript',
                confidence=0.95,
                metadata={'is_enum': True}
            ))
        
        return chunks
