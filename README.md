# Code Chunker

A pragmatic multi-language code parser optimized for LLM applications and RAG systems.

## Features

- **Multi-language support**: Python, JavaScript, TypeScript, Solidity, Go, Rust
- **Optimized for LLMs**: Provides structured output ideal for language models
- **Lightweight**: Minimal dependencies, fast parsing
- **Configurable**: Adjust chunk sizes, confidence thresholds, and more
- **Easy to use**: Simple API with both file and directory parsing

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
    print(f"{chunk.type}: {chunk.name}")

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
