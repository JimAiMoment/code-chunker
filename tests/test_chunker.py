"""
Tests for the main CodeChunker class
"""

import pytest
from pathlib import Path

from code_chunker import CodeChunker
from code_chunker.exceptions import LanguageNotSupportedError


def test_parse_python_code(default_chunker, sample_python_code):
    """測試解析Python程式碼"""
    result = default_chunker.parse(sample_python_code, 'python')
    
    assert result.language == 'python'
    assert len(result.chunks) > 0
    
    # 檢查函數
    function_chunks = [c for c in result.chunks if c.type.value == 'function']
    assert len(function_chunks) >= 2  # hello_world and fetch_data
    
    # 檢查類
    class_chunks = [c for c in result.chunks if c.type.value == 'class']
    assert len(class_chunks) == 1
    assert class_chunks[0].name == 'Person'
    
    # 檢查方法
    method_chunks = [c for c in result.chunks if c.type.value == 'method']
    assert len(method_chunks) == 2  # __init__ and greet


def test_parse_javascript_code(default_chunker, sample_javascript_code):
    """測試解析JavaScript程式碼"""
    result = default_chunker.parse(sample_javascript_code, 'javascript')
    
    assert result.language == 'javascript'
    assert len(result.chunks) > 0
    
    # 檢查函數
    function_chunks = [c for c in result.chunks if c.type.value == 'function']
    assert len(function_chunks) >= 2  # greet and arrowFunc
    
    # 檢查類
    class_chunks = [c for c in result.chunks if c.type.value == 'class']
    assert len(class_chunks) == 1
    assert class_chunks[0].name == 'Calculator'


def test_unsupported_language(default_chunker):
    """測試不支援的語言"""
    with pytest.raises(LanguageNotSupportedError):
        default_chunker.parse("code", "unknown_language")


def test_parse_file(default_chunker, temp_files):
    """測試解析檔案"""
    py_file = temp_files['python']
    result = default_chunker.parse_file(py_file)
    
    assert result.file_path == str(py_file)
    assert result.language == 'python'
    assert len(result.chunks) == 1
    assert result.chunks[0].name == 'test_function'


def test_parse_nonexistent_file(default_chunker):
    """測試解析不存在的檔案"""
    with pytest.raises(FileNotFoundError):
        default_chunker.parse_file('nonexistent.py')


def test_parse_directory(default_chunker, tmp_path):
    """測試解析目錄"""
    # 創建測試檔案
    (tmp_path / "file1.py").write_text("def func1(): pass")
    (tmp_path / "file2.js").write_text("function func2() {}")
    (tmp_path / "file3.txt").write_text("not code")
    
    results = default_chunker.parse_directory(tmp_path)
    
    assert len(results) == 2  # 只有.py和.js文件
    languages = {r.language for r in results}
    assert languages == {'python', 'javascript'}


def test_parse_directory_with_extensions(default_chunker, tmp_path):
    """測試解析目錄時指定副檔名"""
    # 創建測試檔案
    (tmp_path / "file1.py").write_text("def func1(): pass")
    (tmp_path / "file2.js").write_text("function func2() {}")
    
    results = default_chunker.parse_directory(tmp_path, extensions=['.py'])
    
    assert len(results) == 1
    assert results[0].language == 'python'


def test_detect_language(default_chunker):
    """測試語言檢測"""
    assert default_chunker._detect_language(Path("test.py")) == 'python'
    assert default_chunker._detect_language(Path("test.js")) == 'javascript'
    assert default_chunker._detect_language(Path("test.ts")) == 'typescript'
    assert default_chunker._detect_language(Path("test.sol")) == 'solidity'
    assert default_chunker._detect_language(Path("test.go")) == 'go'
    assert default_chunker._detect_language(Path("test.rs")) == 'rust'
    
    with pytest.raises(LanguageNotSupportedError):
        default_chunker._detect_language(Path("test.unknown"))
