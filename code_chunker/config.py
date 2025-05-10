"""
Configuration for code-chunker
"""

from typing import Dict, Any

# 针对不同用途的优化配置
LANGUAGE_CONFIGS = {
    'typescript_react': {
        'max_chunk_size': 1500,  # React 组件通常较小
        'include_jsx': True,
        'extract_props': True,
        'include_comments': True,
    },
    'solidity_contract': {
        'max_chunk_size': 2000,
        'include_comments': True,  # 合约注释很重要
        'extract_modifiers': True,
        'track_visibility': True,
        'detect_security_patterns': True,
    },
    'go_performance': {
        'max_chunk_size': 2500,  # Go 函数可能较长
        'identify_concurrency': True,
        'track_goroutines': True,
        'analyze_channels': True,
    },
    'python_ml': {
        'max_chunk_size': 2000,
        'identify_numpy_ops': True,
        'track_tensor_ops': True,
        'include_comments': True,
    },
    'rust_systems': {
        'max_chunk_size': 2000,
        'track_ownership': True,
        'identify_unsafe': True,
        'include_macros': True,
    }
}

def get_config_for_use_case(language: str, use_case: str = None) -> Dict[str, Any]:
    """获取特定语言和用例的配置
    
    Args:
        language: 编程语言
        use_case: 使用场景
        
    Returns:
        配置字典
    """
    config_key = f"{language}_{use_case}" if use_case else language
    return LANGUAGE_CONFIGS.get(config_key, {}) 