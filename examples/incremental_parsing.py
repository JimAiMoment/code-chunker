#!/usr/bin/env python3
"""
Incremental Parsing Example

This example demonstrates how to use the incremental parsing feature
of the code-chunker library to efficiently update code analysis results
when code changes.
"""

import os
import sys
import time
from pathlib import Path

# Add the parent directory to the path so we can import code_chunker
sys.path.insert(0, str(Path(__file__).parent.parent))

from code_chunker import CodeChunker
from code_chunker.incremental import IncrementalParser


def create_sample_file(file_path: str) -> None:
    """Create a sample Python file for demonstration"""
    code = """
def hello_world():
    \"\"\"Say hello to the world\"\"\"
    print("Hello, World!")

class Person:
    def __init__(self, name: str):
        self.name = name
    
    def greet(self) -> str:
        return f"Hello, I'm {self.name}"

def add(a, b):
    return a + b
"""
    with open(file_path, 'w') as f:
        f.write(code)
    print(f"Created sample file: {file_path}")


def demonstrate_incremental_parsing():
    """Demonstrate incremental parsing functionality"""
    # Create a temporary file for demonstration
    file_path = "temp_example.py"
    create_sample_file(file_path)
    
    try:
        # Create an incremental parser
        parser = IncrementalParser()
        
        # Initial parse
        print("\n=== Initial Parse ===")
        start_time = time.time()
        result1 = parser.full_parse(file_path)
        parse_time = time.time() - start_time
        
        print(f"Parsed {len(result1.chunks)} chunks in {parse_time:.4f} seconds")
        print("Chunks:")
        for chunk in result1.chunks:
            print(f"  - {chunk.type.value}: {chunk.name} (lines {chunk.start_line}-{chunk.end_line})")
        
        # Make a change to the file - modify a function
        print("\n=== Making Changes ===")
        changes = [(13, 14, "def multiply(a, b):\n    return a * b")]
        print("Change: Replace 'add' function with 'multiply' function")
        
        # Apply changes incrementally
        print("\n=== Incremental Parse ===")
        start_time = time.time()
        result2 = parser.parse_incremental(file_path, changes)
        parse_time = time.time() - start_time
        
        print(f"Parsed {len(result2.chunks)} chunks in {parse_time:.4f} seconds")
        print("Chunks:")
        for chunk in result2.chunks:
            print(f"  - {chunk.type.value}: {chunk.name} (lines {chunk.start_line}-{chunk.end_line})")
        
        # Verify the file was actually updated
        with open(file_path, 'r') as f:
            content = f.read()
            if "multiply" in content and "return a * b" in content:
                print("\nFile was successfully updated with the changes.")
            else:
                print("\nWARNING: File was not updated correctly!")
        
        # Make multiple changes
        print("\n=== Making Multiple Changes ===")
        changes = [
            (2, 3, "def hello_world(name):\n    print(f\"Hello, {name}!\")"),
            (13, 14, "def subtract(a, b):\n    return a - b")
        ]
        print("Changes:")
        print("  1. Modify 'hello_world' function to accept a name parameter")
        print("  2. Replace 'multiply' function with 'subtract' function")
        
        # Parse incrementally again
        print("\n=== Second Incremental Parse ===")
        start_time = time.time()
        result3 = parser.parse_incremental(file_path, changes)
        parse_time = time.time() - start_time
        
        print(f"Parsed {len(result3.chunks)} chunks in {parse_time:.4f} seconds")
        print("Chunks:")
        for chunk in result3.chunks:
            print(f"  - {chunk.type.value}: {chunk.name} (lines {chunk.start_line}-{chunk.end_line})")
        
        # Verify the file was actually updated with multiple changes
        with open(file_path, 'r') as f:
            content = f.read()
            if "hello_world(name)" in content and "subtract" in content and "return a - b" in content:
                print("\nFile was successfully updated with multiple changes.")
            else:
                print("\nWARNING: File was not updated correctly with multiple changes!")
        
        # Compare with full parse
        print("\n=== Full Parse (for comparison) ===")
        parser.invalidate_cache(file_path)
        start_time = time.time()
        result4 = parser.full_parse(file_path)
        parse_time = time.time() - start_time
        
        print(f"Parsed {len(result4.chunks)} chunks in {parse_time:.4f} seconds")
        
        # Verify results are the same
        chunks3 = sorted([(c.name, c.type.value) for c in result3.chunks])
        chunks4 = sorted([(c.name, c.type.value) for c in result4.chunks])
        print(f"\nResults match: {chunks3 == chunks4}")
        
        if chunks3 != chunks4:
            print("\nDifferences:")
            print("Incremental parse result:")
            for chunk in chunks3:
                print(f"  - {chunk[1]}: {chunk[0]}")
            print("Full parse result:")
            for chunk in chunks4:
                print(f"  - {chunk[1]}: {chunk[0]}")
        
    finally:
        # Clean up
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"\nRemoved temporary file: {file_path}")


if __name__ == "__main__":
    demonstrate_incremental_parsing() 