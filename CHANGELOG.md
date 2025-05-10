# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.3.2] - 2025-05-11

### Changed
- Translated all Chinese comments to English in the codebase
- Improved code documentation for international users
- Enhanced readability for non-Chinese speaking developers

## [1.3.1] - 2024-06-28

### Fixed
- Fixed TypeScript/React parser to correctly identify and extract React components
- Improved React context type extraction and related context detection
- Fixed React hooks detection for useState, useEffect, and other common hooks
- Enhanced JSX detection for React components and providers
- Fixed ForwardRef component detection and props type extraction
- Added missing `parse` method to TypeScript parser

## [1.3.0] - 2024-06-25

### Added
- Enhanced language support for TypeScript/React, Solidity, and Go
- Added React component, hook, and context detection in TypeScript
- Added smart contract metadata extraction in Solidity (visibility, modifiers, payable)
- Added concurrency pattern detection in Go (goroutines, channels, mutexes)
- Added specialized configurations for different use cases
- Added `get_config_for_use_case` utility function
- Added new ChunkType enums: COMPONENT, HOOK, CONTEXT, TRAIT, IMPL
- Added configuration system for language-specific optimizations

### Changed
- Improved line number calculation in all language parsers
- Updated documentation with examples for enhanced language features
- Improved TypeScript parser to better handle React patterns
- Enhanced Solidity parser with more detailed metadata extraction
- Improved Go parser with concurrency pattern detection

## [1.2.0] - 2024-06-20

### Added
- Implemented incremental parsing functionality for efficient updates
- Added `IncrementalParser` class with caching and change-based parsing
- Smart change detection to identify affected code regions
- Selective reparsing of only affected chunks
- Intelligent merging of updated and unchanged chunks
- Line offset calculation for accurate code positioning
- Cache invalidation mechanisms for manual control
- New example demonstrating incremental parsing usage
- Comprehensive tests for incremental parsing
- Performance benchmarks comparing incremental vs full parsing
- Updated documentation with incremental parsing examples

### Changed
- Improved performance for large file processing
- Enhanced error handling for edge cases
- Optimized memory usage during parsing
- Updated README with incremental parsing examples and use cases
- Refined Python parser to better handle method detection
- Improved handling of imports and exports in incremental updates

### Fixed
- Fixed Python parser method recognition for greet and async methods
- Fixed JavaScript parser import handling
- Fixed Parser class exception handling
- Fixed Rust parser method name issues
- Added TRAIT and IMPL types to ChunkType enum

## [1.1.2] - 2024-06-12

### Fixed
- Corrected GitHub repository links from jimthebeacon to JimAiMoment
- Updated PyPI homepage and documentation links

## [1.1.1] - 2024-06-11

### Added
- Added support for Python 3.13 and 3.14
- Updated CI workflow to test on Python 3.13 and 3.14

### Changed
- Updated development tools configuration for newer Python versions

## [1.1.0] - 2024-06-15

### Added
- Support for Rust language
- Support for Solidity language
- Improved error recovery mechanisms
- Added more configuration options

### Fixed
- Fixed JavaScript class detection
- Improved Python function detection
- Better handling of nested structures

## [1.0.0] - 2024-06-01

### Added
- Initial release
- Support for Python, JavaScript, TypeScript, and Go
- Basic chunking functionality
- File and directory parsing
- Configuration options

## [0.1.0] - 2024-05-10

### Added
- Initial release of Code Chunker
- Support for Python, JavaScript, TypeScript, Solidity, Go, and Rust
- Basic code parsing functionality
- Function, class, method, import, and export extraction
- Configurable chunking options
- Confidence scoring for parsed chunks
- Directory parsing with file filtering
- Examples for basic usage, advanced usage, and RAG integration
- Comprehensive test suite
- Documentation and README

### Features
- Language-agnostic parsing interface
- Modular language processor architecture
- Extensible chunking strategies
- Metadata extraction for code elements
- Line number tracking for all chunks
- Export functionality for JavaScript/TypeScript modules

[Unreleased]: https://github.com/JimAiMoment/code-chunker/compare/v1.3.2...HEAD
[1.3.2]: https://github.com/JimAiMoment/code-chunker/compare/v1.3.1...v1.3.2
[1.3.1]: https://github.com/JimAiMoment/code-chunker/compare/v1.3.0...v1.3.1
[1.3.0]: https://github.com/JimAiMoment/code-chunker/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/JimAiMoment/code-chunker/compare/v1.1.2...v1.2.0
[1.1.2]: https://github.com/JimAiMoment/code-chunker/compare/v1.1.1...v1.1.2
[1.1.1]: https://github.com/JimAiMoment/code-chunker/compare/v1.1.0...v1.1.1
[1.1.0]: https://github.com/JimAiMoment/code-chunker/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/JimAiMoment/code-chunker/compare/v0.1.0...v1.0.0
[0.1.0]: https://github.com/JimAiMoment/code-chunker/releases/tag/v0.1.0
