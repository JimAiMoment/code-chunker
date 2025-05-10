"""
Main entry point for code-chunker
"""

import os
from pathlib import Path
from typing import List, Union, Optional

from .parser import Parser
from .models import ParseResult, ChunkerConfig
from .exceptions import BaseError, LanguageNotSupportedError


class CodeChunker:
    """程式碼分塊器主類"""
    
    def __init__(self, config: Optional[ChunkerConfig] = None):
        self.config = config or ChunkerConfig()
        self.parser = Parser(self.config)
    
    def parse(self, code: str, language: str) -> ParseResult:
        """解析程式碼字串"""
        if not self.parser.is_language_supported(language):
            raise LanguageNotSupportedError(f"Language '{language}' is not supported")
        
        return self.parser.parse(code, language)
    
    def parse_file(self, file_path: Union[str, Path]) -> ParseResult:
        """解析單個檔案"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        language = self._detect_language(file_path)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        result = self.parse(code, language)
        result.file_path = str(file_path)
        return result
    
    def parse_directory(
        self, 
        directory: Union[str, Path], 
        recursive: bool = True,
        extensions: Optional[List[str]] = None
    ) -> List[ParseResult]:
        """解析整個目錄"""
        directory = Path(directory)
        
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        results = []
        
        pattern = "**/*" if recursive else "*"
        for file_path in directory.glob(pattern):
            if file_path.is_file():
                if extensions and file_path.suffix not in extensions:
                    continue
                
                try:
                    result = self.parse_file(file_path)
                    results.append(result)
                except (LanguageNotSupportedError, UnicodeDecodeError):
                    # 跳過不支援的檔案
                    continue
        
        return results
    
    def _detect_language(self, file_path: Path) -> str:
        """根據副檔名檢測語言"""
        extension_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.sol': 'solidity',
            '.go': 'go',
            '.rs': 'rust',
        }
        
        ext = file_path.suffix.lower()
        language = extension_map.get(ext)
        
        if not language:
            raise LanguageNotSupportedError(f"Unknown file extension: {ext}")
        
        return language
