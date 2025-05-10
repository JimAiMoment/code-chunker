"""
Advanced usage example for code-chunker
"""

from code_chunker import CodeChunker, ChunkerConfig
from pathlib import Path

# Example 1: Custom configuration
config = ChunkerConfig(
    max_chunk_size=2000,
    min_chunk_size=100,
    include_comments=True,
    confidence_threshold=0.8,
    language_specific_config={
        'python': {
            'include_docstrings': True,
            'include_type_hints': True
        }
    }
)

chunker = CodeChunker(config=config)

# Example 2: Parse a directory with filters
def parse_project(project_path: str):
    """Parse an entire project directory"""
    results = chunker.parse_directory(
        project_path,
        recursive=True,
        extensions=['.py', '.js', '.ts']
    )
    
    # Group results by language
    by_language = {}
    for result in results:
        lang = result.language
        if lang not in by_language:
            by_language[lang] = []
        by_language[lang].append(result)
    
    # Print summary
    print(f"Project Analysis for: {project_path}")
    print(f"Total files processed: {len(results)}")
    
    for lang, files in by_language.items():
        total_chunks = sum(len(f.chunks) for f in files)
        print(f"\n{lang.capitalize()}:")
        print(f"  Files: {len(files)}")
        print(f"  Total chunks: {total_chunks}")
        
        # Count chunk types
        chunk_types = {}
        for file_result in files:
            for chunk in file_result.chunks:
                chunk_type = chunk.type.value
                chunk_types[chunk_type] = chunk_types.get(chunk_type, 0) + 1
        
        for chunk_type, count in chunk_types.items():
            print(f"  {chunk_type}: {count}")

# Example 3: Analyze code quality
def analyze_code_quality(code: str, language: str):
    """Analyze code quality metrics"""
    result = chunker.parse(code, language)
    
    metrics = {
        'total_chunks': len(result.chunks),
        'functions': 0,
        'classes': 0,
        'methods': 0,
        'imports': len(result.imports),
        'exports': len(result.exports),
        'avg_chunk_size': 0,
        'high_confidence_chunks': 0
    }
    
    total_size = 0
    for chunk in result.chunks:
        chunk_type = chunk.type.value
        if chunk_type == 'function':
            metrics['functions'] += 1
        elif chunk_type == 'class':
            metrics['classes'] += 1
        elif chunk_type == 'method':
            metrics['methods'] += 1
        
        total_size += len(chunk.code)
        
        if chunk.confidence >= 0.9:
            metrics['high_confidence_chunks'] += 1
    
    if metrics['total_chunks'] > 0:
        metrics['avg_chunk_size'] = total_size / metrics['total_chunks']
    
    return metrics

# Example 4: Extract specific patterns
def find_async_functions(code: str):
    """Find all async functions in the code"""
    result = chunker.parse(code, 'javascript')
    
    async_functions = []
    for chunk in result.chunks:
        if chunk.type.value == 'function' and 'async' in chunk.code:
            async_functions.append(chunk)
    
    return async_functions

# Example usage
if __name__ == '__main__':
    # Test with a sample TypeScript code
    typescript_code = """
    interface User {
        id: number;
        name: string;
        email: string;
    }
    
    class UserService {
        private users: User[] = [];
        
        async addUser(user: User): Promise<void> {
            this.users.push(user);
        }
        
        getUserById(id: number): User | undefined {
            return this.users.find(user => user.id === id);
        }
    }
    
    export default UserService;
    """
    
    result = chunker.parse(typescript_code, 'typescript')
    
    print("TypeScript Analysis:")
    print(f"Total chunks: {len(result.chunks)}")
    
    for chunk in result.chunks:
        print(f"\n{chunk.type.value}: {chunk.name}")
        if chunk.metadata:
            print(f"Metadata: {chunk.metadata}")
    
    # Analyze quality metrics
    metrics = analyze_code_quality(typescript_code, 'typescript')
    print(f"\nCode Quality Metrics:")
    for key, value in metrics.items():
        print(f"  {key}: {value}")
