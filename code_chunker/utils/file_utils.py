"""File utility functions"""

import os
from pathlib import Path
from typing import List


def get_supported_extensions() -> List[str]:
    """Get supported file extensions"""
    return ['.py', '.js', '.ts', '.go', '.rs', '.sol']


def is_binary_file(file_path: str) -> bool:
    """Check if file is binary"""
    with open(file_path, 'rb') as f:
        chunk = f.read(1024)
        return b'\0' in chunk


def normalize_newlines(text: str) -> str:
    """Normalize newlines"""
    return text.replace('\r\n', '\n').replace('\r', '\n')
