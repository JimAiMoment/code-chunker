"""
Pytest configuration and fixtures
"""

import pytest
from pathlib import Path

from code_chunker import CodeChunker, ChunkerConfig


@pytest.fixture
def default_chunker():
    """創建預設的chunker實例"""
    return CodeChunker()


@pytest.fixture
def custom_config():
    """創建自定義配置"""
    return ChunkerConfig(
        max_chunk_size=2000,
        min_chunk_size=50,
        include_comments=True,
        confidence_threshold=0.7
    )


@pytest.fixture
def custom_chunker(custom_config):
    """創建自定義配置的chunker實例"""
    return CodeChunker(config=custom_config)


@pytest.fixture
def sample_python_code():
    """提供Python測試代碼"""
    return '''
def hello_world():
    """Say hello to the world"""
    print("Hello, World!")

class Person:
    def __init__(self, name: str):
        self.name = name
    
    def greet(self) -> str:
        return f"Hello, I'm {self.name}"

async def fetch_data(url: str):
    # Fetch data from URL
    pass
'''


@pytest.fixture
def sample_javascript_code():
    """提供JavaScript測試代碼"""
    return '''
function greet(name) {
    console.log(`Hello, ${name}!`);
}

const arrowFunc = (x, y) => x + y;

class Calculator {
    constructor() {
        this.result = 0;
    }
    
    add(x, y) {
        this.result = x + y;
        return this.result;
    }
}

export default Calculator;
'''


@pytest.fixture
def temp_files(tmp_path):
    """創建臨時測試檔案"""
    files = {}
    
    # Python文件
    py_file = tmp_path / "test.py"
    py_file.write_text('''
def test_function():
    return "test"
''')
    files['python'] = py_file
    
    # JavaScript文件
    js_file = tmp_path / "test.js"
    js_file.write_text('''
function testFunction() {
    return "test";
}
''')
    files['javascript'] = js_file
    
    return files
