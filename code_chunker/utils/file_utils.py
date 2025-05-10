"""
File handling utilities
"""

from pathlib import Path
from typing import List


def get_supported_extensions() -> List[str]:
    """獲取支援的檔案副檔名"""
    return ['.py', '.js', '.jsx', '.ts', '.tsx', '.sol', '.go', '.rs']


def is_binary_file(file_path: Path) -> bool:
    """檢查是否為二進制檔案"""
    try:
        with open(file_path, 'tr') as check_file:
            check_file.read()
            return False
    except UnicodeDecodeError:
        return True


def normalize_line_endings(content: str) -> str:
    """統一換行符"""
    return content.replace('\r\n', '\n').replace('\r', '\n')
