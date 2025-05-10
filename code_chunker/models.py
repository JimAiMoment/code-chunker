"""
Data models for code-chunker
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional, Any


class ChunkType(Enum):
    FUNCTION = "function"
    CLASS = "class"
    METHOD = "method"
    IMPORT = "import"
    EXPORT = "export"
    VARIABLE = "variable"
    COMMENT = "comment"
    UNKNOWN = "unknown"


@dataclass
class CodeChunk:
    """表示一個程式碼塊"""
    type: ChunkType
    name: Optional[str]
    code: str
    start_line: int
    end_line: int
    language: str
    confidence: float = 1.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class Import:
    """表示導入語句"""
    module: str
    names: List[str]
    alias: Optional[str] = None
    line_number: int = 0


@dataclass
class ParseResult:
    """解析結果"""
    language: str
    file_path: Optional[str]
    chunks: List[CodeChunk]
    imports: List[Import]
    exports: List[str]
    raw_code: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ChunkerConfig:
    """分塊器配置"""
    max_chunk_size: int = 1500
    min_chunk_size: int = 100
    overlap_size: int = 50
    include_comments: bool = True
    include_imports: bool = True
    confidence_threshold: float = 0.8
    language_specific_config: Dict[str, Dict] = None
    
    def __post_init__(self):
        if self.language_specific_config is None:
            self.language_specific_config = {}
