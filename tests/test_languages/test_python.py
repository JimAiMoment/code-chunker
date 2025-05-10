"""
Tests for Python language processor
"""

import pytest

from code_chunker.languages.python import PythonProcessor
from code_chunker.models import ChunkerConfig, ChunkType


@pytest.fixture
def python_processor():
    """創建Python處理器實例"""
    config = ChunkerConfig()
    return PythonProcessor(config)


def test_extract_function(python_processor):
    """測試提取函數"""
    code = '''
def simple_function():
    pass

def function_with_args(arg1, arg2):
    return arg1 + arg2

async def async_function():
    await something()
'''
    
    chunks = python_processor.extract_chunks(code)
    
    assert len(chunks) == 3
    assert all(chunk.type == ChunkType.FUNCTION for chunk in chunks)
    
    names = {chunk.name for chunk in chunks}
    assert names == {'simple_function', 'function_with_args', 'async_function'}


def test_extract_class(python_processor):
    """測試提取類"""
    code = '''
class SimpleClass:
    pass

class InheritedClass(BaseClass):
    def method(self):
        pass
'''
    
    chunks = python_processor.extract_chunks(code)
    
    class_chunks = [c for c in chunks if c.type == ChunkType.CLASS]
    assert len(class_chunks) == 2
    
    names = {chunk.name for chunk in class_chunks}
    assert names == {'SimpleClass', 'InheritedClass'}


def test_extract_method(python_processor):
    """測試提取方法"""
    code = '''
class MyClass:
    def method1(self):
        pass
    
    async def async_method(self):
        pass
    
    def method_with_decorator(self):
        pass
'''
    
    chunks = python_processor.extract_chunks(code)
    
    method_chunks = [c for c in chunks if c.type == ChunkType.METHOD]
    assert len(method_chunks) == 3
    
    names = {chunk.name for chunk in method_chunks}
    assert names == {'method1', 'async_method', 'method_with_decorator'}


def test_extract_imports(python_processor):
    """測試提取導入語句"""
    code = '''
import os
import sys
from pathlib import Path
from typing import List, Dict
import numpy as np
from collections import defaultdict
'''
    
    imports = python_processor.extract_imports(code)
    
    assert len(imports) == 6
    
    # 檢查簡單import
    os_import = next(i for i in imports if 'os' in i.names)
    assert os_import.module == ''
    
    # 檢查from import
    path_import = next(i for i in imports if 'Path' in i.names)
    assert path_import.module == 'pathlib'
    
    # 檢查多個導入
    typing_import = next(i for i in imports if i.module == 'typing')
    assert set(typing_import.names) == {'List', 'Dict'}


def test_indentation_handling(python_processor):
    """測試縮排處理"""
    code = '''
def outer_function():
    def inner_function():
        pass
    
    class InnerClass:
        def inner_method(self):
            pass
'''
    
    chunks = python_processor.extract_chunks(code)
    
    # 應該找到外部函數
    outer_func = next(c for c in chunks if c.name == 'outer_function')
    assert outer_func.type == ChunkType.FUNCTION
    
    # 內部函數應該被識別為function而不是method
    inner_func = next(c for c in chunks if c.name == 'inner_function')
    assert inner_func.type == ChunkType.FUNCTION
    
    # 類內的方法應該被識別為method
    inner_method = next(c for c in chunks if c.name == 'inner_method')
    assert inner_method.type == ChunkType.METHOD
