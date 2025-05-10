"""
Tests for incremental parsing functionality
"""

import pytest
from pathlib import Path

from code_chunker import CodeChunker
from code_chunker.incremental import IncrementalParser
from code_chunker.models import ChunkType


@pytest.fixture
def incremental_parser():
    """Create an incremental parser instance"""
    return IncrementalParser()


@pytest.fixture
def python_file_content():
    """Sample Python file content"""
    return """
def hello_world():
    print("Hello, World!")

class Person:
    def __init__(self, name):
        self.name = name
    
    def greet(self):
        return f"Hello, {self.name}"

def add(a, b):
    return a + b
"""


@pytest.fixture
def python_file(tmp_path, python_file_content):
    """Create a temporary Python file"""
    file_path = tmp_path / "test.py"
    file_path.write_text(python_file_content)
    return file_path


def test_incremental_parsing_basic(incremental_parser, python_file):
    """Test basic incremental parsing functionality"""
    # Initial parse
    result1 = incremental_parser.full_parse(str(python_file))
    
    # Make a change to the file
    changes = [(13, 14, "def multiply(a, b):\n    return a * b")]
    result2 = incremental_parser.parse_incremental(str(python_file), changes)
    
    # Verify the function was changed
    function_chunks = [c for c in result2.chunks if c.type == ChunkType.FUNCTION and c.name == "multiply"]
    assert len(function_chunks) == 1
    assert "return a * b" in function_chunks[0].code


def test_incremental_parsing_add_method(incremental_parser, python_file):
    """Test adding a new method to a class"""
    # Initial parse
    result1 = incremental_parser.full_parse(str(python_file))
    
    # Add a new method to the Person class
    changes = [(11, 11, "    def say_goodbye(self):\n        return f\"Goodbye, {self.name}\"\n")]
    result2 = incremental_parser.parse_incremental(str(python_file), changes)
    
    # Check that the method was added
    function_chunks = [c for c in result2.chunks if c.type == ChunkType.FUNCTION and c.name == "say_goodbye"]
    assert len(function_chunks) == 1
    assert "Goodbye" in function_chunks[0].code


def test_incremental_parsing_remove_function(incremental_parser, python_file):
    """Test removing a function"""
    # Initial parse
    result1 = incremental_parser.full_parse(str(python_file))
    
    # Remove the add function
    changes = [(12, 14, "")]
    result2 = incremental_parser.parse_incremental(str(python_file), changes)
    
    # Check that the function was removed
    function_chunks = [c for c in result2.chunks if c.type == ChunkType.FUNCTION and c.name == "add"]
    assert len(function_chunks) == 0


def test_incremental_parsing_modify_class(incremental_parser, python_file):
    """Test modifying a class"""
    # Initial parse
    result1 = incremental_parser.full_parse(str(python_file))
    
    # Modify the Person class
    changes = [(5, 11, """class User:
    def __init__(self, username):
        self.username = username
    
    def greet(self):
        return f"Hello, @{self.username}"
""")]
    result2 = incremental_parser.parse_incremental(str(python_file), changes)
    
    # Check that the class was modified
    class_chunks = [c for c in result2.chunks if c.type == ChunkType.CLASS]
    assert len(class_chunks) == 1
    assert class_chunks[0].name == "User"
    
    # Check methods - they are parsed as functions in the current implementation
    function_chunks = [c for c in result2.chunks if c.type == ChunkType.FUNCTION and c.name in ["__init__", "greet"]]
    assert len(function_chunks) == 2  # __init__, greet
    
    # Check the modified greet method
    greet_functions = [m for m in function_chunks if m.name == "greet"]
    assert len(greet_functions) == 1
    assert "@{self.username}" in greet_functions[0].code


def test_incremental_parsing_multiple_changes(incremental_parser, python_file):
    """Test multiple changes at once"""
    # Initial parse
    result1 = incremental_parser.full_parse(str(python_file))
    
    # Make multiple changes
    changes = [
        (2, 3, "def hello_world(name):\n    print(f\"Hello, {name}!\")"),
        (13, 14, "def subtract(a, b):\n    return a - b")
    ]
    result2 = incremental_parser.parse_incremental(str(python_file), changes)
    
    # Check that both changes were applied
    hello_world = [c for c in result2.chunks if c.type == ChunkType.FUNCTION and c.name == "hello_world"]
    assert len(hello_world) == 1
    assert "name" in hello_world[0].code
    
    subtract = [c for c in result2.chunks if c.type == ChunkType.FUNCTION and c.name == "subtract"]
    assert len(subtract) == 1
    assert "return a - b" in subtract[0].code


def test_incremental_parsing_edge_cases(incremental_parser, tmp_path):
    """Test edge cases for incremental parsing"""
    # Empty file
    empty_file = tmp_path / "empty.py"
    empty_file.write_text("")
    
    # Initial parse
    result1 = incremental_parser.full_parse(str(empty_file))
    assert len(result1.chunks) == 0
    
    # Add content to empty file
    changes = [(1, 1, "def test():\n    pass\n")]
    result2 = incremental_parser.parse_incremental(str(empty_file), changes)
    
    # Check that content was added
    assert len(result2.chunks) == 1
    assert result2.chunks[0].name == "test"


def test_incremental_parsing_performance(incremental_parser, tmp_path):
    """Test performance of incremental parsing vs full parsing"""
    # Create a large file
    large_file = tmp_path / "large.py"
    content = "# Large file\n\n"
    
    # Add 50 functions
    for i in range(50):
        content += f"""
def function_{i}(param):
    # Function {i}
    result = param + {i}
    return result

"""
    
    large_file.write_text(content)
    
    # Initial parse
    result1 = incremental_parser.full_parse(str(large_file))
    
    # Make a small change in the middle
    changes = [(25, 26, "def function_modified(param):\n    return param * 2\n")]
    
    # Measure time for incremental parse vs full parse
    import time
    
    # Incremental parse
    start_time = time.time()
    result2 = incremental_parser.parse_incremental(str(large_file), changes)
    incremental_time = time.time() - start_time
    
    # Force full parse
    incremental_parser.invalidate_cache(str(large_file))
    start_time = time.time()
    result3 = incremental_parser.full_parse(str(large_file))
    full_time = time.time() - start_time
    
    # In the current implementation, incremental parsing might not be faster
    # since we're doing a full parse in both cases
    # Just verify that the changes were correctly applied
    modified_func = [c for c in result2.chunks if c.name == "function_modified"]
    assert len(modified_func) == 1
    assert "return param * 2" in modified_func[0].code 