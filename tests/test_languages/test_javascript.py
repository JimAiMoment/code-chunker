"""
Tests for JavaScript language processor
"""

import pytest

from code_chunker.languages.javascript import JavaScriptProcessor
from code_chunker.models import ChunkerConfig, ChunkType


@pytest.fixture
def js_processor():
    """創建JavaScript處理器實例"""
    config = ChunkerConfig()
    return JavaScriptProcessor(config)


def test_extract_function(js_processor):
    """測試提取函數"""
    code = '''
function simpleFunction() {
    console.log("Hello");
}

async function asyncFunction() {
    await doSomething();
}

const arrowFunction = () => {
    return "arrow";
};

const asyncArrow = async (param) => {
    return await fetch(param);
};
'''
    
    chunks = js_processor.extract_chunks(code)
    function_chunks = [c for c in chunks if c.type == ChunkType.FUNCTION]
    
    assert len(function_chunks) == 4
    
    names = {chunk.name for chunk in function_chunks}
    assert names == {'simpleFunction', 'asyncFunction', 'arrowFunction', 'asyncArrow'}


def test_extract_class(js_processor):
    """測試提取類"""
    code = '''
class SimpleClass {
    constructor() {
        this.value = 0;
    }
}

class ExtendedClass extends BaseClass {
    method() {
        return this.value;
    }
}
'''
    
    chunks = js_processor.extract_chunks(code)
    class_chunks = [c for c in chunks if c.type == ChunkType.CLASS]
    
    assert len(class_chunks) == 2
    
    names = {chunk.name for chunk in class_chunks}
    assert names == {'SimpleClass', 'ExtendedClass'}


def test_extract_imports(js_processor):
    """測試提取導入語句"""
    code = '''
import React from 'react';
import { useState, useEffect } from 'react';
import * as utils from './utils';
import './styles.css';
'''
    
    imports = js_processor.extract_imports(code)
    
    assert len(imports) == 4
    
    # 檢查默認導入
    react_import = next(i for i in imports if i.module == 'react' and 'React' in i.names)
    assert react_import is not None
    
    # 檢查命名導入
    hooks_import = next(i for i in imports if i.module == 'react' and 'useState' in i.names)
    assert 'useEffect' in hooks_import.names


def test_extract_exports(js_processor):
    """測試提取導出語句"""
    code = '''
export const value = 42;
export function exportedFunction() {}
export default class DefaultClass {}
export { namedExport };
'''
    
    exports = js_processor.extract_exports(code)
    
    assert len(exports) >= 3
    assert 'value' in exports
    assert 'exportedFunction' in exports
    assert 'DefaultClass' in exports


def test_arrow_function_end_detection(js_processor):
    """測試箭頭函數結束位置檢測"""
    code = '''
const simpleArrow = () => 42;

const blockArrow = () => {
    return {
        value: 42
    };
};

const inlineArrow = () => ({ value: 42 });
'''
    
    chunks = js_processor.extract_chunks(code)
    function_chunks = [c for c in chunks if c.type == ChunkType.FUNCTION]
    
    assert len(function_chunks) == 3
    
    # 檢查每個函數的完整性
    for chunk in function_chunks:
        assert chunk.code.strip().endswith(';') or chunk.code.strip().endswith('}')
