"""
Data models for code-chunker
"""

from dataclasses import dataclass, field
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
    TRAIT = "trait"
    IMPL = "impl"
    COMPONENT = "component"  # React 组件
    HOOK = "hook"           # React Hook
    CONTEXT = "context"     # React Context
    HOC = "hoc"            # 高阶组件
    PROVIDER = "provider"   # Context Provider
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
    
    # 自定义配置参数
    # TypeScript/React 相关
    include_jsx: bool = False
    extract_props: bool = False
    
    # Solidity 相关
    extract_modifiers: bool = False
    track_visibility: bool = False
    detect_security_patterns: bool = False
    
    # Go 相关
    identify_concurrency: bool = False
    track_goroutines: bool = False
    analyze_channels: bool = False
    
    # Python ML 相关
    identify_numpy_ops: bool = False
    track_tensor_ops: bool = False
    
    # Rust 相关
    track_ownership: bool = False
    identify_unsafe: bool = False
    include_macros: bool = False
    
    # 其他自定义配置
    custom_config: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.language_specific_config is None:
            self.language_specific_config = {}
    
    def get_value(self, key: str, default: Any = None) -> Any:
        """获取配置值，优先从自定义配置中获取"""
        if key in self.custom_config:
            return self.custom_config[key]
        return getattr(self, key, default)
