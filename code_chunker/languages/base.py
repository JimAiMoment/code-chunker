"""Base language parser"""

from abc import ABC, abstractmethod
from typing import List, Dict, Pattern
import re

from ..models import CodeChunk, Import, ParseResult, ChunkerConfig


class LanguageParser(ABC):
    """Base class for language parsers"""
    
    def __init__(self, config: ChunkerConfig):
        self.config = config
        self.patterns = self._get_patterns()
    
    @abstractmethod
    def _get_patterns(self) -> Dict[str, Pattern]:
        """Get language-specific regex patterns"""
        pass
    
    def preprocess(self, code: str) -> str:
        """Preprocess code"""
        # Default: no processing
        return code
    
    def postprocess(self, result: ParseResult) -> ParseResult:
        """Postprocess result"""
        # Filter out low confidence chunks
        if self.config.confidence_threshold > 0:
            result.chunks = [
                chunk for chunk in result.chunks 
                if chunk.confidence >= self.config.confidence_threshold
            ]
        
        return result
    
    @abstractmethod
    def extract_chunks(self, code: str) -> List[CodeChunk]:
        """Extract code chunks"""
        pass
    
    @abstractmethod
    def extract_imports(self, code: str) -> List[Import]:
        """Extract import statements"""
        pass
    
    def extract_exports(self, code: str) -> List[str]:
        """Extract export statements"""
        # Default: return empty list
        return []
    
    def _find_block_end(self, lines: List[str], start_index: int, indent_level: int) -> int:
        """Find code block end position (for indented languages)"""
        for i in range(start_index + 1, len(lines)):
            line = lines[i]
            if line.strip() == '':
                continue
            
            current_indent = len(line) - len(line.lstrip())
            if current_indent <= indent_level:
                return i - 1
        
        return len(lines) - 1
    
    def _find_matching_brace(self, code: str, start_pos: int) -> int:
        """Find matching brace"""
        brace_count = 1
        pos = start_pos + 1
        
        while pos < len(code) and brace_count > 0:
            if code[pos] == '{':
                brace_count += 1
            elif code[pos] == '}':
                brace_count -= 1
            pos += 1
        
        return pos - 1
