"""
Base language processor
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Pattern
import re

from ..models import CodeChunk, Import, ParseResult, ChunkerConfig


class LanguageProcessor(ABC):
    """語言處理器基類"""
    
    def __init__(self, config: ChunkerConfig):
        self.config = config
        self.patterns = self._get_patterns()
    
    @abstractmethod
    def _get_patterns(self) -> Dict[str, Pattern]:
        """獲取語言特定的正則模式"""
        pass
    
    def preprocess(self, code: str) -> str:
        """預處理程式碼"""
        # 預設不做處理
        return code
    
    def postprocess(self, result: ParseResult) -> ParseResult:
        """後處理結果"""
        # 過濾低信心度的chunks
        if self.config.confidence_threshold > 0:
            result.chunks = [
                chunk for chunk in result.chunks 
                if chunk.confidence >= self.config.confidence_threshold
            ]
        
        return result
    
    @abstractmethod
    def extract_chunks(self, code: str) -> List[CodeChunk]:
        """提取程式碼塊"""
        pass
    
    @abstractmethod
    def extract_imports(self, code: str) -> List[Import]:
        """提取導入語句"""
        pass
    
    def extract_exports(self, code: str) -> List[str]:
        """提取導出語句"""
        # 預設返回空列表
        return []
    
    def _find_block_end(self, lines: List[str], start_index: int, indent_level: int) -> int:
        """找到程式碼塊結束位置（用於縮排語言）"""
        for i in range(start_index + 1, len(lines)):
            line = lines[i]
            if line.strip() == '':
                continue
            
            current_indent = len(line) - len(line.lstrip())
            if current_indent <= indent_level:
                return i - 1
        
        return len(lines) - 1
    
    def _find_matching_brace(self, code: str, start_pos: int) -> int:
        """找到匹配的大括號"""
        brace_count = 1
        pos = start_pos + 1
        
        while pos < len(code) and brace_count > 0:
            if code[pos] == '{':
                brace_count += 1
            elif code[pos] == '}':
                brace_count -= 1
            pos += 1
        
        return pos - 1
