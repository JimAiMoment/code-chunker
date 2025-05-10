# Code Chunker

A pragmatic multi-language code parser optimized for LLM applications and RAG systems.

## Features

- **Multi-language support**: Python, JavaScript, TypeScript, Solidity, Go, Rust
- **Optimized for LLMs**: Provides structured output ideal for language models
- **Lightweight**: Minimal dependencies, fast parsing
- **Configurable**: Adjust chunk sizes, confidence thresholds, and more
- **Easy to use**: Simple API with both file and directory parsing
- **Incremental parsing**: Efficiently update parse results when code changes
- **Enhanced language support**:
  - **TypeScript/React**: Component, Hook, and Context detection
  - **Solidity**: Smart contract metadata extraction (visibility, modifiers, payable)
  - **Go**: Concurrency pattern detection (goroutines, channels, mutexes)

## Installation

```bash
pip install code-chunker
```

## Quick Start

```python
from code_chunker import CodeChunker

# Initialize the chunker
chunker = CodeChunker()

# Parse a code string
code = """
def hello_world():
    print("Hello, World!")
"""

result = chunker.parse(code, language='python')

# Print the chunks
for chunk in result.chunks:
    print(f"{chunk.type.value}: {chunk.name} (lines {chunk.start_line}-{chunk.end_line})")

# Parse a file
result = chunker.parse_file('example.py')

# Parse a directory
results = chunker.parse_directory('src/')
```

## Configuration

```python
from code_chunker import CodeChunker, ChunkerConfig

config = ChunkerConfig(
    max_chunk_size=2000,
    min_chunk_size=100,
    include_comments=True,
    confidence_threshold=0.8
)

chunker = CodeChunker(config=config)
```

## Incremental Parsing

Incremental parsing allows you to efficiently update parse results when code changes, without reparsing the entire file.

```python
from code_chunker import CodeChunker, IncrementalParser

# Initialize the incremental parser
incremental_parser = IncrementalParser()

# First parse (full parse)
result1 = incremental_parser.full_parse("path/to/file.py")

# After file changes, perform an incremental parse
result2 = incremental_parser.incremental_parse("path/to/file.py")

# Compare the results
print(f"Full parse chunks: {len(result1.chunks)}")
print(f"Incremental parse chunks: {len(result2.chunks)}")
```

## Enhanced Language Support

### TypeScript/React Support

Code Chunker provides specialized support for React components, hooks, and contexts:

```python
from code_chunker import CodeChunker, ChunkerConfig, get_config_for_use_case

# Get React-optimized configuration
config = ChunkerConfig(**get_config_for_use_case('typescript', 'react'))
chunker = CodeChunker(config=config)

# Parse React component
result = chunker.parse(react_code, language='typescript')

# Filter for React components
components = [chunk for chunk in result.chunks if chunk.type.value == 'component']
for component in components:
    print(f"Component: {component.name} (type: {component.metadata.get('component_type')})")
```

### Solidity Smart Contract Support

Enhanced metadata extraction for smart contracts:

```python
from code_chunker import CodeChunker, ChunkerConfig, get_config_for_use_case

# Get Solidity-optimized configuration
config = ChunkerConfig(**get_config_for_use_case('solidity', 'contract'))
chunker = CodeChunker(config=config)

# Parse Solidity contract
result = chunker.parse(contract_code, language='solidity')

# Find payable functions
payable_functions = [
    chunk for chunk in result.chunks 
    if chunk.type.value == 'function' and chunk.metadata.get('is_payable', False)
]
```

### Go Concurrency Pattern Detection

Automatically detect concurrency patterns in Go code:

```python
from code_chunker import CodeChunker, ChunkerConfig, get_config_for_use_case

# Get Go-optimized configuration
config = ChunkerConfig(**get_config_for_use_case('go', 'performance'))
chunker = CodeChunker(config=config)

# Parse Go code
result = chunker.parse(go_code, language='go')

# Find functions with goroutines
concurrent_funcs = [
    chunk for chunk in result.chunks 
    if chunk.type.value in ['function', 'method'] 
    and 'goroutines' in chunk.metadata.get('concurrency_patterns', {})
]
```

## Supported Languages

- Python (.py)
- JavaScript (.js, .jsx)
- TypeScript (.ts, .tsx)
- Solidity (.sol)
- Go (.go)
- Rust (.rs)

## Examples

The `examples/` directory contains several examples demonstrating different features:

### Basic Usage

Simple parsing examples:

```bash
python examples/basic_usage.py
```

### Advanced Usage

Custom configuration and analysis:

```bash
python examples/advanced_usage.py
```

### Incremental Parsing

Efficient parsing of code changes:

```bash
python examples/incremental_parsing.py
```

### RAG Integration

Integration with RAG systems:

```bash
python examples/rag_integration.py
```

### Edge Cases

Testing various edge cases across languages:

```bash
python examples/edge_cases.py
```

### Performance Analysis

Analyze parsing performance:

```bash
python examples/performance_analysis.py
```

### Code Quality Analysis

Analyze code quality metrics:

```bash
python examples/quality_analysis.py <file_path>
```

### Visualization

Generate code structure visualization:

```bash
python examples/visualization.py <file_path>
```

## API Reference

### CodeChunker

The main class for parsing code.

```python
chunker = CodeChunker(config=None)
```

#### Methods

- `parse(code: str, language: str) -> ParseResult`: Parse a code string
- `parse_file(file_path: Union[str, Path]) -> ParseResult`: Parse a file
- `parse_directory(directory: Union[str, Path], recursive: bool = True, extensions: Optional[List[str]] = None) -> List[ParseResult]`: Parse a directory

### IncrementalParser

For efficient incremental parsing.

```python
parser = IncrementalParser(chunker=None)
```

#### Methods

- `full_parse(file_path: str) -> ParseResult`: Perform a full parse and cache the result
- `parse_incremental(file_path: str, changes: List[Tuple[int, int, str]]) -> ParseResult`: Parse incrementally based on changes
- `invalidate_cache(file_path: Optional[str] = None) -> None`: Invalidate cache for a file or all files

#### How Incremental Parsing Works

1. **Initial Parse**: The first parse of a file is a full parse, which is cached
2. **Change Detection**: When changes are made, only affected code regions are identified
3. **Selective Reparsing**: Only affected chunks are reparsed, preserving the rest
4. **Result Merging**: Updated chunks are merged with unchanged chunks
5. **Smart Caching**: Results are cached for future incremental updates

### ParseResult

The result of parsing code.

#### Attributes

- `language: str`: The programming language
- `file_path: Optional[str]`: Path to the source file
- `chunks: List[CodeChunk]`: List of code chunks
- `imports: List[Import]`: List of imports
- `exports: List[str]`: List of exports
- `raw_code: str`: The original code

### CodeChunk

Represents a piece of code.

#### Attributes

- `type: ChunkType`: The type of chunk (function, class, etc.)
- `name: Optional[str]`: The name of the chunk
- `code: str`: The actual code
- `start_line: int`: Starting line number
- `end_line: int`: Ending line number
- `language: str`: Programming language
- `confidence: float`: Confidence score (0-1)
- `metadata: Dict[str, Any]`: Additional metadata

## Dependencies

- For basic usage: No external dependencies
- For performance analysis: `psutil`
- For visualization: Modern web browser to view generated HTML

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

1. Clone the repository
2. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
3. Run tests:
   ```bash
   pytest
   ```
4. Format code:
   ```bash
   black code_chunker/
   ```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you find this project helpful, consider supporting its development:

- ⭐ Star this repository
- 🐛 Report bugs and suggest features
- 🤝 Submit pull requests
- 💰 EVM(ETH, ARB, BNB, OP..etc): `0x8f74959530dba14394b27faac92955aa96927e8b`
## Acknowledgments

Thanks to all contributors and the open-source community for their support.
