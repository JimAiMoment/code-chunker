"""
Go language processor
"""

import re
from typing import List, Dict, Pattern

from .base import LanguageParser
from ..models import CodeChunk, Import, ChunkType


class GoParser(LanguageParser):
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
            # 并发模式
            'goroutine': re.compile(
                r'go\s+(\w+\([^)]*\))',
                re.MULTILINE
            ),
            'channel_make': re.compile(
                r'make\s*\(\s*chan\s+([^,\)]+)(?:\s*,\s*(\d+))?\s*\)',
                re.MULTILINE
            ),
            'channel_op': re.compile(
                r'([^:=\s]+)\s*(?:<-|:=\s*<-|=\s*<-)\s*([^;]+)',
                re.MULTILINE
            ),
            'select_stmt': re.compile(
                r'select\s*\{([^}]+)\}',
                re.MULTILINE | re.DOTALL
            ),
            'mutex_lock': re.compile(
                r'(\w+)\.(?:Lock|RLock)\(\)',
                re.MULTILINE
            ),
            'mutex_unlock': re.compile(
                r'(\w+)\.(?:Unlock|RUnlock)\(\)',
                re.MULTILINE
            ),
            'waitgroup': re.compile(
                r'(\w+)\.(?:Add|Done|Wait)\([^)]*\)',
                re.MULTILINE
            ),
        }
    
    def extract_chunks(self, code: str) -> List[CodeChunk]:
        chunks = []
        
        # 提取函數
        for match in self._get_patterns()['function'].finditer(code):
            name = match.group(1)
            start_pos = match.start()
            start_line = code[:start_pos].count('\n') + 1  # 1-indexed
            
            end_pos = self._find_matching_brace(code, match.end() - 1)
            end_line = code[:end_pos].count('\n') + 1  # 1-indexed
            
            function_code = code[start_pos:end_pos + 1]
            
            # 检查函数中的并发模式
            concurrency_patterns = self._detect_concurrency_patterns(function_code)
            
            chunks.append(CodeChunk(
                type=ChunkType.FUNCTION,
                name=name,
                code=function_code,
                start_line=start_line,
                end_line=end_line,
                language='go',
                confidence=0.95,
                metadata={
                    'concurrency_patterns': concurrency_patterns
                }
            ))
        
        # 提取方法
        for match in self._get_patterns()['method'].finditer(code):
            receiver = match.group(1)
            name = match.group(2)
            start_pos = match.start()
            start_line = code[:start_pos].count('\n') + 1  # 1-indexed
            
            end_pos = self._find_matching_brace(code, match.end() - 1)
            end_line = code[:end_pos].count('\n') + 1  # 1-indexed
            
            method_code = code[start_pos:end_pos + 1]
            
            # 检查方法中的并发模式
            concurrency_patterns = self._detect_concurrency_patterns(method_code)
            
            chunks.append(CodeChunk(
                type=ChunkType.METHOD,
                name=name,
                code=method_code,
                start_line=start_line,
                end_line=end_line,
                language='go',
                confidence=0.95,
                metadata={
                    'receiver': receiver,
                    'concurrency_patterns': concurrency_patterns
                }
            ))
        
        # 提取結構體
        for match in self._get_patterns()['struct'].finditer(code):
            name = match.group(1)
            start_pos = match.start()
            start_line = code[:start_pos].count('\n') + 1  # 1-indexed
            
            end_pos = self._find_matching_brace(code, match.end() - 1)
            end_line = code[:end_pos].count('\n') + 1  # 1-indexed
            
            struct_code = code[start_pos:end_pos + 1]
            
            # 检查结构体是否包含 sync 相关字段
            has_mutex = 'sync.Mutex' in struct_code or 'sync.RWMutex' in struct_code
            has_waitgroup = 'sync.WaitGroup' in struct_code
            has_channel = 'chan ' in struct_code
            
            chunks.append(CodeChunk(
                type=ChunkType.CLASS,
                name=name,
                code=struct_code,
                start_line=start_line,
                end_line=end_line,
                language='go',
                confidence=0.95,
                metadata={
                    'go_type': 'struct',
                    'has_mutex': has_mutex,
                    'has_waitgroup': has_waitgroup,
                    'has_channel': has_channel
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
    
    def _detect_concurrency_patterns(self, code: str) -> Dict[str, List]:
        """检测代码中的并发模式"""
        patterns = {
            'goroutines': [],
            'channels': [],
            'select_statements': [],
            'mutex_operations': [],
            'waitgroup_operations': []
        }
        
        # 检测 goroutine
        for match in self._get_patterns()['goroutine'].finditer(code):
            goroutine_call = match.group(1)
            patterns['goroutines'].append(goroutine_call)
        
        # 检测 channel 创建
        for match in self._get_patterns()['channel_make'].finditer(code):
            channel_type = match.group(1)
            buffer_size = match.group(2) if match.group(2) else "0"
            patterns['channels'].append({
                'type': channel_type,
                'buffered': buffer_size != "0",
                'buffer_size': buffer_size
            })
        
        # 检测 channel 操作
        for match in self._get_patterns()['channel_op'].finditer(code):
            left = match.group(1)
            right = match.group(2)
            patterns['channels'].append({
                'operation': 'send' if '<-' in left else 'receive',
                'channel': left if '<-' in right else right
            })
        
        # 检测 select 语句
        for match in self._get_patterns()['select_stmt'].finditer(code):
            select_body = match.group(1)
            cases = select_body.count('case')
            has_default = 'default:' in select_body
            patterns['select_statements'].append({
                'cases': cases,
                'has_default': has_default
            })
        
        # 检测 mutex 操作
        for match in self._get_patterns()['mutex_lock'].finditer(code):
            mutex_var = match.group(1)
            patterns['mutex_operations'].append({
                'variable': mutex_var,
                'operation': 'lock'
            })
        
        for match in self._get_patterns()['mutex_unlock'].finditer(code):
            mutex_var = match.group(1)
            patterns['mutex_operations'].append({
                'variable': mutex_var,
                'operation': 'unlock'
            })
        
        # 检测 WaitGroup 操作
        for match in self._get_patterns()['waitgroup'].finditer(code):
            wg_var = match.group(1)
            operation = match.group(0)
            op_type = 'add' if '.Add' in operation else 'done' if '.Done' in operation else 'wait'
            patterns['waitgroup_operations'].append({
                'variable': wg_var,
                'operation': op_type
            })
        
        # 过滤空列表，保持结果简洁
        return {k: v for k, v in patterns.items() if v}
    
    def extract_imports(self, code: str) -> List[Import]:
        imports = []
        
        for match in self._get_patterns()['import'].finditer(code):
            single_import = match.group(1)
            multi_imports = match.group(2)
            line_number = code[:match.start()].count('\n') + 1  # 1-indexed
            
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

    def parse(self, code: str) -> List[CodeChunk]:
        """Parse Go code"""
        return self.extract_chunks(code)
