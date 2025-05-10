"""
Performance analysis for code-chunker
"""

import time
import os
from pathlib import Path
import sys

# Add the parent directory to the path so we can import code_chunker
sys.path.insert(0, str(Path(__file__).parent.parent))

from code_chunker import CodeChunker
from code_chunker.incremental import IncrementalParser

try:
    import psutil
    import statistics
    HAVE_PSUTIL = True
except ImportError:
    HAVE_PSUTIL = False
    print("psutil not installed. Memory usage statistics will not be available.")
    print("Install with: pip install psutil")


def analyze_performance(file_path: str, iterations: int = 5):
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
        if HAVE_PSUTIL:
            process = psutil.Process(os.getpid())
            start_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Timing
        start_time = time.time()
        result = chunker.parse(code, language)
        end_time = time.time()
        
        # Record end memory
        if HAVE_PSUTIL:
            end_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_usage.append(end_memory - start_memory)
        
        times.append(end_time - start_time)
    
    # Statistics
    stats = {
        'file_path': file_path,
        'file_size': file_size,
        'language': language,
        'chunks_count': len(result.chunks),
        'avg_time': sum(times) / len(times),
        'min_time': min(times),
        'max_time': max(times),
        'lines_per_second': len(code.split('\n')) / (sum(times) / len(times)),
        'bytes_per_second': file_size / (sum(times) / len(times)),
    }
    
    if HAVE_PSUTIL and memory_usage:
        stats.update({
            'avg_memory': sum(memory_usage) / len(memory_usage),
            'std_time': statistics.stdev(times) if len(times) > 1 else 0,
        })
    
    return stats


def generate_large_file(file_path: str, num_functions: int):
    """Generate a large Python file with many functions"""
    with open(file_path, 'w') as f:
        f.write("# Large file with many functions\n\n")
        f.write("import os\nimport sys\nimport math\nimport random\nimport time\n\n")
        f.write("# Global variables\nGLOBAL_VAR = 100\nDEBUG = False\n\n")
        
        # Add some utility functions
        f.write("""
def utility_function_1(a, b):
    \"\"\"Utility function 1\"\"\"
    return a + b

def utility_function_2(a, b):
    \"\"\"Utility function 2\"\"\"
    return a * b

class BaseClass:
    \"\"\"Base class for demonstration\"\"\"
    
    def __init__(self, name):
        self.name = name
        self._value = 0
    
    def get_value(self):
        return self._value
    
    def set_value(self, value):
        self._value = value
    
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, new_value):
        self._value = new_value
    
    def __str__(self):
        return f"{self.name}: {self._value}"

""")
        
        # Add many functions with different complexity
        for i in range(num_functions):
            complexity = i % 5
            
            if complexity == 0:
                # Simple function
                f.write(f"""
def function_{i}_simple(param):
    # Function {i} - Simple
    result = param + {i}
    return result

""")
            elif complexity == 1:
                # Medium function with conditionals
                f.write(f"""
def function_{i}_conditional(param1, param2):
    # Function {i} - Conditional
    if param1 > param2:
        return param1 - param2
    elif param1 < param2:
        return param2 - param1
    else:
        return param1 * 2

""")
            elif complexity == 2:
                # Function with loop
                f.write(f"""
def function_{i}_loop(items):
    # Function {i} - Loop
    total = 0
    for item in items:
        if item % 2 == 0:
            total += item
        else:
            total -= item
    return total * {i}

""")
            elif complexity == 3:
                # Function with nested structure
                f.write(f"""
def function_{i}_nested(data, threshold={i}):
    # Function {i} - Nested
    results = []
    for group in data:
        group_results = []
        for item in group:
            if item > threshold:
                processed = item * 2
                if processed % 3 == 0:
                    group_results.append(processed)
                else:
                    group_results.append(processed // 2)
        if group_results:
            results.append(sum(group_results) / len(group_results))
    return results

""")
            else:
                # Class with methods
                f.write(f"""
class Class_{i}(BaseClass):
    \"\"\"Class {i} for demonstration\"\"\"
    
    def __init__(self, name, initial_value={i}):
        super().__init__(name)
        self._value = initial_value
        self.created_at = time.time()
    
    def process_data(self, data):
        \"\"\"Process the given data\"\"\"
        result = []
        for item in data:
            result.append(item * self._value)
        return result
    
    def calculate_metric(self):
        \"\"\"Calculate a metric based on the value\"\"\"
        return math.sqrt(self._value) if self._value > 0 else 0
    
    @staticmethod
    def utility_method(param):
        \"\"\"Utility method\"\"\"
        return param * 2

""")


def benchmark_large_files():
    """Benchmark performance on large files"""
    sizes = [100, 300, 500]  # 增加文件大小
    
    for size in sizes:
        # 生成大型Python文件
        temp_file = f"temp_large_{size}.py"
        generate_large_file(temp_file, size)
        
        try:
            # 分析性能
            result = analyze_performance(temp_file, iterations=3)  # 减少迭代次数
            
            # 输出结果
            print(f"\nSize: {size} functions/classes")
            print(f"File size: {result['file_size'] / 1024:.2f} KB")
            print(f"Chunks: {result['chunks_count']}")
            print(f"Avg time: {result['avg_time']:.4f} seconds")
            print(f"Lines/sec: {result['lines_per_second']:.0f}")
            if HAVE_PSUTIL:
                print(f"Memory: {result.get('avg_memory', 'N/A'):.2f} MB")
        finally:
            # 清理临时文件
            if os.path.exists(temp_file):
                os.remove(temp_file)


def benchmark_incremental_parsing():
    """Benchmark incremental parsing performance"""
    print("\n=== Incremental Parsing Performance ===")
    
    # 生成测试文件 - 使用更大的文件
    temp_file = "temp_incremental.py"
    generate_large_file(temp_file, 300)  # 300个函数/类
    
    try:
        # 创建增量解析器
        parser = IncrementalParser()
        
        # 初始解析
        print("\nInitial parse:")
        start_time = time.time()
        result1 = parser.full_parse(temp_file)
        initial_time = time.time() - start_time
        print(f"Time: {initial_time:.4f} seconds")
        print(f"Chunks: {len(result1.chunks)}")
        
        # 非常小的改动 - 只修改一行代码
        tiny_change = [(100, 101, "    result = param + 1000  # Modified line")]
        
        print("\nIncremental parse (tiny change - single line):")
        start_time = time.time()
        result2 = parser.parse_incremental(temp_file, tiny_change)
        tiny_change_time = time.time() - start_time
        print(f"Time: {tiny_change_time:.4f} seconds")
        print(f"Chunks: {len(result2.chunks)}")
        print(f"Speed improvement: {initial_time / tiny_change_time:.1f}x faster than full parse")
        
        # 小改动 - 修改一个函数
        small_change = [(150, 154, """
def modified_function(param):
    # Modified function
    result = param * 2
    return result

""")]
        
        print("\nIncremental parse (small change - one function):")
        start_time = time.time()
        result3 = parser.parse_incremental(temp_file, small_change)
        small_change_time = time.time() - start_time
        print(f"Time: {small_change_time:.4f} seconds")
        print(f"Chunks: {len(result3.chunks)}")
        print(f"Speed improvement: {initial_time / small_change_time:.1f}x faster than full parse")
        
        # 中等改动 - 修改多个不相邻的行
        medium_changes = [
            (50, 51, "    return param1 * param2 + 100  # Modified line"),
            (200, 201, "    return math.pow(param, 3)  # Modified line"),
            (350, 351, "    return sum(result) / len(result) if result else 0  # Modified line")
        ]
        
        print("\nIncremental parse (medium changes - multiple lines):")
        start_time = time.time()
        result4 = parser.parse_incremental(temp_file, medium_changes)
        medium_change_time = time.time() - start_time
        print(f"Time: {medium_change_time:.4f} seconds")
        print(f"Chunks: {len(result4.chunks)}")
        print(f"Speed improvement: {initial_time / medium_change_time:.1f}x faster than full parse")
        
        # 大改动 - 修改多个函数
        large_changes = []
        for i in range(10, 20):
            large_changes.append((
                i * 20, 
                i * 20 + 10, 
                f"""
def modified_function_{i}(param1, param2, param3=None):
    # Heavily modified function {i}
    if param3 is None:
        param3 = param1 + param2
    
    result = param1 * param2 / (param3 if param3 != 0 else 1)
    return round(result, 2)

"""
            ))
        
        print("\nIncremental parse (large changes - multiple functions):")
        start_time = time.time()
        result5 = parser.parse_incremental(temp_file, large_changes)
        large_change_time = time.time() - start_time
        print(f"Time: {large_change_time:.4f} seconds")
        print(f"Chunks: {len(result5.chunks)}")
        print(f"Speed improvement: {initial_time / large_change_time:.1f}x faster than full parse")
        
        # 强制全量解析进行比较
        print("\nForced full parse (for comparison):")
        parser.invalidate_cache(temp_file)
        start_time = time.time()
        result6 = parser.full_parse(temp_file)
        forced_full_time = time.time() - start_time
        print(f"Time: {forced_full_time:.4f} seconds")
        print(f"Chunks: {len(result6.chunks)}")
        
    finally:
        # 清理临时文件
        if os.path.exists(temp_file):
            os.remove(temp_file)


if __name__ == '__main__':
    print("=== Performance Analysis ===")
    print("Testing parsing performance on files of different sizes...")
    benchmark_large_files()
    
    print("\nTesting incremental parsing performance...")
    benchmark_incremental_parsing() 