"""
Core parser module for code-chunker
"""

import re
from typing import Dict, Type, List, Optional

from .models import ParseResult, CodeChunk, ChunkerConfig
from .languages.base import LanguageParser
from .exceptions import ParserError, LanguageNotSupportedError
from .strategies.base import ChunkingStrategy


class Parser:
    """Core parser"""
    
    def __init__(self, config=None):
        self.config = config
        self.language_parsers: Dict[str, Type[LanguageParser]] = {}
        self.chunking_strategy: Optional[ChunkingStrategy] = None
        self.load_language_parsers()  # 自动加载语言解析器
    
    def register_language(self, language: str, parser_class: Type[LanguageParser]):
        """Register a language parser"""
        self.language_parsers[language] = parser_class
    
    def load_language_parsers(self):
        """Load language processors"""
        from .languages import python, javascript, typescript, go, rust, solidity
        
        self.register_language('python', python.PythonParser)
        self.register_language('javascript', javascript.JavaScriptParser)
        self.register_language('typescript', typescript.TypeScriptParser)
        self.register_language('go', go.GoParser)
        self.register_language('rust', rust.RustParser)
        self.register_language('solidity', solidity.SolidityParser)
    
    def is_language_supported(self, language: str) -> bool:
        """Check if language is supported"""
        return language in self.language_parsers
    
    def parse(self, code: str, language: str) -> ParseResult:
        """Parse code"""
        if not self.is_language_supported(language):
            raise LanguageNotSupportedError(f"Language not supported: {language}")
        
        # Preprocessing
        parser_class = self.language_parsers[language]
        parser = parser_class(self.config) if self.config else parser_class()
        
        # Extract chunks
        chunks = parser.parse(code)
        
        # Extract imports
        imports = parser.extract_imports(code)
        
        # Extract exports
        exports = parser.extract_exports(code)
        
        # Post-processing
        if self.chunking_strategy:
            chunks = self.chunking_strategy.chunk(code, language)
        
        return ParseResult(
            chunks=chunks,
            imports=imports,
            exports=exports,
            language=language
        )
