"""
Basic usage example for code-chunker
"""

from code_chunker import CodeChunker

# Create a chunker instance
chunker = CodeChunker()

# Example 1: Parse a simple Python function
python_code = """
def calculate_fibonacci(n):
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

class MathUtils:
    @staticmethod
    def is_prime(num):
        if num < 2:
            return False
        for i in range(2, int(num ** 0.5) + 1):
            if num % i == 0:
                return False
        return True
"""

result = chunker.parse(python_code, 'python')

print(f"Language: {result.language}")
print(f"Number of chunks: {len(result.chunks)}")
print("\nChunks found:")
for chunk in result.chunks:
    print(f"- {chunk.type.value}: {chunk.name} (lines {chunk.start_line}-{chunk.end_line})")

# Example 2: Parse a JavaScript file
js_code = """
function greet(name) {
    console.log(`Hello, ${name}!`);
}

const Calculator = class {
    constructor() {
        this.result = 0;
    }
    
    add(x, y) {
        this.result = x + y;
        return this.result;
    }
};

export { greet, Calculator };
"""

js_result = chunker.parse(js_code, 'javascript')

print(f"\nJavaScript chunks: {len(js_result.chunks)}")
for chunk in js_result.chunks:
    print(f"- {chunk.type.value}: {chunk.name}")

# Example 3: Parse a file
# Uncomment the following lines to test with a real file
# file_result = chunker.parse_file('path/to/your/file.py')
# print(f"\nFile: {file_result.file_path}")
# print(f"Chunks: {len(file_result.chunks)}")
