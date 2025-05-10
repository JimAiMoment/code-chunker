"""
Tests for the Parser class
"""

import pytest

from code_chunker.parser import Parser
from code_chunker.models import ChunkerConfig
from code_chunker.exceptions import ParserError


def test_parser_initialization():
    """測試Parser初始化"""
    config = ChunkerConfig()
    parser = Parser(config)
    
    assert parser.config == config
    assert len(parser._processors) > 0
    assert 'python' in parser._processors
    assert 'javascript' in parser._processors


def test_is_language_supported():
    """測試語言支援檢查"""
    config = ChunkerConfig()
    parser = Parser(config)
    
    assert parser.is_language_supported('python')
    assert parser.is_language_supported('javascript')
    assert not parser.is_language_supported('unknown')


def test_parse_with_invalid_language():
    """測試解析不支援的語言"""
    config = ChunkerConfig()
    parser = Parser(config)
    
    with pytest.raises(ParserError):
        parser.parse("code", "unknown_language")


def test_parse_with_processor_error():
    """測試處理器錯誤"""
    config = ChunkerConfig()
    parser = Parser(config)
    
    # 測試無效的Python代碼
    with pytest.raises(ParserError):
        # 這個會導致正則表達式錯誤
        parser.parse("def function(:\n    pass", "python")
