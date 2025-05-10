"""
Core parser module for code-chunker
"""

import re
from typing import Dict, Type, List

from .models import ParseResult, CodeChunk, ChunkerConfig
from .languages.base import LanguageProcessor
from .exceptions import ParserError


class Parser:
    """核心解析器"""
    
    def __init__(self, config: ChunkerConfig):
        self.config = config
        self._processors: Dict[str, LanguageProcessor] = {}
        self._load_processors()
    
    def _load_processors(self):
        """載入語言處理器"""
        from .languages import (
            PythonProcessor,
            JavaScriptProcessor,
            TypeScriptProcessor,
            SolidityProcessor,
            GoProcessor,
            RustProcessor
        )
        
        processors = {
            'python': PythonProcessor,
            'javascript': JavaScriptProcessor,
            'typescript': TypeScriptProcessor,
            'solidity': SolidityProcessor,
            'go': GoProcessor,
            'rust': RustProcessor,
        }
        
        for lang, processor_class in processors.items():
            self._processors[lang] = processor_class(self.config)
    
    def is_language_supported(self, language: str) -> bool:
        """檢查語言是否支援"""
        return language in self._processors
    
    def parse(self, code: str, language: str) -> ParseResult:
        """解析程式碼"""
        processor = self._processors.get(language)
        if not processor:
            raise ParserError(f"No processor found for language: {language}")
        
        try:
            # 預處理
            processed_code = processor.preprocess(code)
            
            # 提取chunks
            chunks = processor.extract_chunks(processed_code)
            
            # 提取imports
            imports = processor.extract_imports(processed_code)
            
            # 提取exports
            exports = processor.extract_exports(processed_code)
            
            # 後處理
            result = ParseResult(
                language=language,
                file_path=None,
                chunks=chunks,
                imports=imports,
                exports=exports,
                raw_code=code
            )
            
            return processor.postprocess(result)
            
        except Exception as e:
            raise ParserError(f"Error parsing {language} code: {str(e)}")
