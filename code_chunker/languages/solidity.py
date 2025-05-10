"""
Solidity language processor
"""

import re
from typing import List, Dict, Pattern, Set

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
            'state_variable': re.compile(
                r'(?:public|private|internal)\s+(?:constant\s+)?(\w+)(?:\s+[^=;]+)?(?:\s*=\s*[^;]+)?\s*;',
                re.MULTILINE
            ),
            'constructor': re.compile(
                r'constructor\s*\([^)]*\)\s*(?:public|internal)?[^{]*\{',
                re.MULTILINE
            ),
            'visibility': re.compile(
                r'(public|private|internal|external)',
                re.MULTILINE
            ),
            'modifiers': re.compile(
                r'(view|pure|payable|constant|virtual|override)',
                re.MULTILINE
            ),
            'custom_modifiers': re.compile(
                r'(?:function\s+\w+\s*\([^)]*\)[^{]*)\s+(\w+)(?:\([^)]*\))?\s*(?=[{;])',
                re.MULTILINE
            ),
        }
    
    def extract_chunks(self, code: str) -> List[CodeChunk]:
        chunks = []
        
        # 提取合約
        for match in self._get_patterns()['contract'].finditer(code):
            name = match.group(1)
            start_pos = match.start()
            start_line = code[:start_pos].count('\n') + 1  # 1-indexed
            
            end_pos = self._find_matching_brace(code, match.end() - 1)
            end_line = code[:end_pos].count('\n') + 1  # 1-indexed
            
            contract_code = code[start_pos:end_pos + 1]
            
            # 提取合约继承关系
            inheritance = []
            is_match = re.search(r'contract\s+\w+\s+is\s+([^{]+)', contract_code)
            if is_match:
                inheritance_str = is_match.group(1).strip()
                inheritance = [i.strip() for i in inheritance_str.split(',')]
            
            # 检查是否是抽象合约
            is_abstract = 'abstract' in contract_code[:match.start() - start_pos + 10]
            
            chunks.append(CodeChunk(
                type=ChunkType.CLASS,
                name=name,
                code=contract_code,
                start_line=start_line,
                end_line=end_line,
                language='solidity',
                confidence=0.95,
                metadata={
                    'contract_type': 'contract',
                    'is_abstract': is_abstract,
                    'inheritance': inheritance
                }
            ))
        
        # 提取介面
        for match in self._get_patterns()['interface'].finditer(code):
            name = match.group(1)
            start_pos = match.start()
            start_line = code[:start_pos].count('\n') + 1  # 1-indexed
            
            end_pos = self._find_matching_brace(code, match.end() - 1)
            end_line = code[:end_pos].count('\n') + 1  # 1-indexed
            
            interface_code = code[start_pos:end_pos + 1]
            
            # 提取接口继承关系
            inheritance = []
            is_match = re.search(r'interface\s+\w+\s+is\s+([^{]+)', interface_code)
            if is_match:
                inheritance_str = is_match.group(1).strip()
                inheritance = [i.strip() for i in inheritance_str.split(',')]
            
            chunks.append(CodeChunk(
                type=ChunkType.CLASS,
                name=name,
                code=interface_code,
                start_line=start_line,
                end_line=end_line,
                language='solidity',
                confidence=0.95,
                metadata={
                    'contract_type': 'interface',
                    'inheritance': inheritance
                }
            ))
        
        # 提取库
        for match in self._get_patterns()['library'].finditer(code):
            name = match.group(1)
            start_pos = match.start()
            start_line = code[:start_pos].count('\n') + 1  # 1-indexed
            
            end_pos = self._find_matching_brace(code, match.end() - 1)
            end_line = code[:end_pos].count('\n') + 1  # 1-indexed
            
            library_code = code[start_pos:end_pos + 1]
            
            chunks.append(CodeChunk(
                type=ChunkType.CLASS,
                name=name,
                code=library_code,
                start_line=start_line,
                end_line=end_line,
                language='solidity',
                confidence=0.95,
                metadata={'contract_type': 'library'}
            ))
        
        # 提取函數
        for match in self._get_patterns()['function'].finditer(code):
            name = match.group(1)
            start_pos = match.start()
            start_line = code[:start_pos].count('\n') + 1  # 1-indexed
            
            # 檢查是否為函數聲明（以分號結尾）
            if code[match.end() - 1] == ';':
                end_pos = match.end()
                end_line = start_line
                is_declaration = True
            else:
                end_pos = self._find_matching_brace(code, match.end() - 1)
                end_line = code[:end_pos].count('\n') + 1  # 1-indexed
                is_declaration = False
            
            function_code = code[start_pos:end_pos]
            
            # 提取函数可见性
            visibility = 'internal'  # 默认可见性
            visibility_match = self._get_patterns()['visibility'].search(function_code)
            if visibility_match:
                visibility = visibility_match.group(1)
            
            # 提取函数修饰符
            modifiers = []
            for mod_match in self._get_patterns()['modifiers'].finditer(function_code):
                modifiers.append(mod_match.group(1))
            
            # 提取自定义修饰符
            for custom_mod_match in self._get_patterns()['custom_modifiers'].finditer(function_code):
                modifiers.append(custom_mod_match.group(1))
            
            # 检查是否为 payable 函数
            is_payable = 'payable' in modifiers
            
            # 检查是否为 view 或 pure 函数
            is_view = 'view' in modifiers
            is_pure = 'pure' in modifiers
            
            # 检查是否为 virtual 或 override 函数
            is_virtual = 'virtual' in modifiers
            is_override = 'override' in modifiers
            
            chunks.append(CodeChunk(
                type=ChunkType.FUNCTION,
                name=name,
                code=function_code,
                start_line=start_line,
                end_line=end_line,
                language='solidity',
                confidence=0.95,
                metadata={
                    'visibility': visibility,
                    'modifiers': modifiers,
                    'is_payable': is_payable,
                    'is_view': is_view,
                    'is_pure': is_pure,
                    'is_virtual': is_virtual,
                    'is_override': is_override,
                    'is_declaration': is_declaration
                }
            ))
        
        # 提取构造函数
        for match in self._get_patterns()['constructor'].finditer(code):
            start_pos = match.start()
            start_line = code[:start_pos].count('\n') + 1  # 1-indexed
            
            end_pos = self._find_matching_brace(code, match.end() - 1)
            end_line = code[:end_pos].count('\n') + 1  # 1-indexed
            
            constructor_code = code[start_pos:end_pos + 1]
            
            # 提取构造函数可见性
            visibility = 'public'  # 默认可见性
            visibility_match = self._get_patterns()['visibility'].search(constructor_code)
            if visibility_match:
                visibility = visibility_match.group(1)
            
            # 提取构造函数修饰符
            modifiers = []
            for mod_match in self._get_patterns()['modifiers'].finditer(constructor_code):
                modifiers.append(mod_match.group(1))
            
            # 提取自定义修饰符
            for custom_mod_match in self._get_patterns()['custom_modifiers'].finditer(constructor_code):
                modifiers.append(custom_mod_match.group(1))
            
            # 检查是否为 payable 构造函数
            is_payable = 'payable' in modifiers
            
            chunks.append(CodeChunk(
                type=ChunkType.FUNCTION,
                name='constructor',
                code=constructor_code,
                start_line=start_line,
                end_line=end_line,
                language='solidity',
                confidence=0.95,
                metadata={
                    'is_constructor': True,
                    'visibility': visibility,
                    'modifiers': modifiers,
                    'is_payable': is_payable
                }
            ))
        
        # 提取修飾符
        for match in self._get_patterns()['modifier'].finditer(code):
            name = match.group(1)
            start_pos = match.start()
            start_line = code[:start_pos].count('\n') + 1  # 1-indexed
            
            end_pos = self._find_matching_brace(code, match.end() - 1)
            end_line = code[:end_pos].count('\n') + 1  # 1-indexed
            
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
        for match in self._get_patterns()['event'].finditer(code):
            name = match.group(1)
            start_pos = match.start()
            start_line = code[:start_pos].count('\n') + 1  # 1-indexed
            end_line = start_line
            
            event_code = match.group(0)
            
            # 提取事件参数
            params_match = re.search(r'\((.*?)\)', event_code)
            params = []
            if params_match:
                params_str = params_match.group(1).strip()
                if params_str:
                    params = [p.strip() for p in params_str.split(',')]
            
            # 检查是否有 indexed 参数
            indexed_params = []
            for param in params:
                if 'indexed' in param:
                    param_name = param.split()[-1]
                    indexed_params.append(param_name)
            
            chunks.append(CodeChunk(
                type=ChunkType.VARIABLE,
                name=name,
                code=event_code,
                start_line=start_line,
                end_line=end_line,
                language='solidity',
                confidence=0.95,
                metadata={
                    'is_event': True,
                    'params': params,
                    'indexed_params': indexed_params
                }
            ))
        
        # 提取状态变量
        for match in self._get_patterns()['state_variable'].finditer(code):
            name = match.group(1)
            start_pos = match.start()
            start_line = code[:start_pos].count('\n') + 1  # 1-indexed
            end_line = start_line
            
            var_code = match.group(0)
            
            # 提取可见性
            visibility = 'internal'  # 默认可见性
            visibility_match = self._get_patterns()['visibility'].search(var_code)
            if visibility_match:
                visibility = visibility_match.group(1)
            
            # 检查是否为常量
            is_constant = 'constant' in var_code
            
            chunks.append(CodeChunk(
                type=ChunkType.VARIABLE,
                name=name,
                code=var_code,
                start_line=start_line,
                end_line=end_line,
                language='solidity',
                confidence=0.9,
                metadata={
                    'is_state_variable': True,
                    'visibility': visibility,
                    'is_constant': is_constant
                }
            ))
        
        return chunks
    
    def extract_imports(self, code: str) -> List[Import]:
        imports = []
        
        for match in self._get_patterns()['import'].finditer(code):
            path = match.group(1) or match.group(2)
            line_number = code[:match.start()].count('\n') + 1  # 1-indexed
            
            imports.append(Import(
                module=path,
                names=[],
                line_number=line_number
            ))
        
        return imports
    
    def _extract_modifiers(self, code: str) -> List[str]:
        """提取函数修饰符"""
        modifiers = []
        
        # 提取内置修饰符
        for mod_match in self._get_patterns()['modifiers'].finditer(code):
            modifiers.append(mod_match.group(1))
        
        # 提取自定义修饰符
        for custom_mod_match in self._get_patterns()['custom_modifiers'].finditer(code):
            modifiers.append(custom_mod_match.group(1))
        
        return modifiers
    
    def _extract_visibility(self, code: str) -> str:
        """提取函数可见性"""
        visibility = 'internal'  # 默认可见性
        visibility_match = self._get_patterns()['visibility'].search(code)
        if visibility_match:
            visibility = visibility_match.group(1)
        return visibility

    def parse(self, code: str) -> List[CodeChunk]:
        """Parse Solidity code"""
        return self.extract_chunks(code)
