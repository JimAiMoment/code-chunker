"""
Solidity language processor
"""

import re
from typing import List, Dict, Pattern

from .base import LanguageParser
from ..models import CodeChunk, Import, ChunkType


class SolidityParser(LanguageParser):
    """Solidity語言處理器"""
    
    def _get_patterns(self) -> Dict[str, Pattern]:
        return {
            'contract': re.compile(
                r'(?:abstract\s+)?contract\s+(\w+)(?:\s+is\s+[^{]+)?\s*\{',
                re.MULTILINE
            ),
            'interface': re.compile(
                r'interface\s+(\w+)(?:\s+is\s+[^{]+)?\s*\{',
                re.MULTILINE
            ),
            'library': re.compile(
                r'library\s+(\w+)\s*\{',
                re.MULTILINE
            ),
            'function': re.compile(
                r'function\s+(\w+)\s*\([^)]*\)\s*(?:public|private|internal|external)?[^{;]*[{;]',
                re.MULTILINE
            ),
            'modifier': re.compile(
                r'modifier\s+(\w+)\s*\([^)]*\)\s*\{',
                re.MULTILINE
            ),
            'event': re.compile(
                r'event\s+(\w+)\s*\([^)]*\);',
                re.MULTILINE
            ),
            'import': re.compile(
                r'import\s+(?:"([^"]+)"|\'([^\']+)\')\s*;',
                re.MULTILINE
            ),
            'pragma': re.compile(
                r'pragma\s+solidity\s+([^;]+);',
                re.MULTILINE
            ),
        }
    
    def extract_chunks(self, code: str) -> List[CodeChunk]:
        chunks = []
        
        # 提取合約
        for match in self.patterns['contract'].finditer(code):
            name = match.group(1)
            start_pos = match.start()
            start_line = code[:start_pos].count('\n')
            
            end_pos = self._find_matching_brace(code, match.end() - 1)
            end_line = code[:end_pos].count('\n')
            
            contract_code = code[start_pos:end_pos + 1]
            
            chunks.append(CodeChunk(
                type=ChunkType.CLASS,
                name=name,
                code=contract_code,
                start_line=start_line,
                end_line=end_line,
                language='solidity',
                confidence=0.95,
                metadata={'contract_type': 'contract'}
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
                language='solidity',
                confidence=0.95,
                metadata={'contract_type': 'interface'}
            ))
        
        # 提取函數
        for match in self.patterns['function'].finditer(code):
            name = match.group(1)
            start_pos = match.start()
            start_line = code[:start_pos].count('\n')
            
            # 檢查是否為函數聲明（以分號結尾）
            if code[match.end() - 1] == ';':
                end_pos = match.end()
                end_line = start_line
            else:
                end_pos = self._find_matching_brace(code, match.end() - 1)
                end_line = code[:end_pos].count('\n')
            
            function_code = code[start_pos:end_pos]
            
            chunks.append(CodeChunk(
                type=ChunkType.FUNCTION,
                name=name,
                code=function_code,
                start_line=start_line,
                end_line=end_line,
                language='solidity',
                confidence=0.95
            ))
        
        # 提取修飾符
        for match in self.patterns['modifier'].finditer(code):
            name = match.group(1)
            start_pos = match.start()
            start_line = code[:start_pos].count('\n')
            
            end_pos = self._find_matching_brace(code, match.end() - 1)
            end_line = code[:end_pos].count('\n')
            
            modifier_code = code[start_pos:end_pos + 1]
            
            chunks.append(CodeChunk(
                type=ChunkType.FUNCTION,
                name=name,
                code=modifier_code,
                start_line=start_line,
                end_line=end_line,
                language='solidity',
                confidence=0.9,
                metadata={'is_modifier': True}
            ))
        
        # 提取事件
        for match in self.patterns['event'].finditer(code):
            name = match.group(1)
            start_pos = match.start()
            start_line = code[:start_pos].count('\n')
            end_line = start_line
            
            event_code = match.group(0)
            
            chunks.append(CodeChunk(
                type=ChunkType.VARIABLE,
                name=name,
                code=event_code,
                start_line=start_line,
                end_line=end_line,
                language='solidity',
                confidence=0.95,
                metadata={'is_event': True}
            ))
        
        return chunks
    
    def extract_imports(self, code: str) -> List[Import]:
        imports = []
        
        for match in self.patterns['import'].finditer(code):
            path = match.group(1) or match.group(2)
            line_number = code[:match.start()].count('\n')
            
            imports.append(Import(
                module=path,
                names=[],
                line_number=line_number
            ))
        
        return imports
