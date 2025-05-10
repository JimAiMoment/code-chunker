"""
Performance analysis for code-chunker
"""

import time
import os
from pathlib import Path
from code_chunker import CodeChunker
import psutil
import statistics

def analyze_performance(file_path: str, iterations: int = 10):
    """Analyze parsing performance"""
    chunker = CodeChunker()
    
    # Read file content
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()
    
    file_size = os.path.getsize(file_path)
    language = chunker._detect_language(Path(file_path))
    
    # Warm up
    chunker.parse(code, language)
    
    # Performance testing
    times = []
    memory_usage = []
    
    for i in range(iterations):
        # Record start memory
        process = psutil.Process(os.getpid())
        start_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Timing
        start_time = time.time()
        result = chunker.parse(code, language)
        end_time = time.time()
        
        # Record end memory
        end_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        times.append(end_time - start_time)
        memory_usage.append(end_memory - start_memory)
    
    # Statistics
    return {
        'file_path': file_path,
        'file_size': file_size,
        'language': language,
        'chunks_count': len(result.chunks),
        'avg_time': statistics.mean(times),
        'min_time': min(times),
        'max_time': max(times),
        'std_time': statistics.stdev(times) if len(times) > 1 else 0,
        'avg_memory': statistics.mean(memory_usage),
        'lines_per_second': len(code.split('\n')) / statistics.mean(times),
        'bytes_per_second': file_size / statistics.mean(times),
    }

def benchmark_large_files():
    """Test performance with large files"""
    # Generate large test files
    large_code = """
def function_{i}(param_{i}):
    '''Function {i} documentation'''
    result = param_{i} * 2
    if result > 100:
        return result / 2
    else:
        return result * 2

class Class_{i}:
    def __init__(self):
        self.value = {i}
    
    def method_{i}(self, x):
        return x + self.value
"""
    
    test_sizes = [100, 500, 1000, 5000]  # Different test sizes
    
    results = []
    
    for size in test_sizes:
        # Generate test code
        code_parts = [large_code.format(i=i) for i in range(size)]
        full_code = '\n'.join(code_parts)
        
        # Write to temporary file
        temp_file = f'temp_test_{size}.py'
        with open(temp_file, 'w') as f:
            f.write(full_code)
        
        try:
            # Analyze performance
            result = analyze_performance(temp_file, iterations=5)
            results.append(result)
            
            print(f"\nSize: {size} functions/classes")
            print(f"File size: {result['file_size'] / 1024:.2f} KB")
            print(f"Chunks: {result['chunks_count']}")
            print(f"Avg time: {result['avg_time']:.4f} seconds")
            print(f"Lines/sec: {result['lines_per_second']:.0f}")
            print(f"Memory: {result['avg_memory']:.2f} MB")
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    return results

if __name__ == '__main__':
    benchmark_large_files() 