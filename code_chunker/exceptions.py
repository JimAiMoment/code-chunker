"""
Custom exceptions for code-chunker
"""


class ChunkerError(Exception):
    """基礎異常類"""
    pass


class LanguageNotSupportedError(ChunkerError):
    """語言不支援異常"""
    pass


class ParserError(ChunkerError):
    """解析錯誤異常"""
    pass


class FileProcessingError(ChunkerError):
    """檔案處理錯誤"""
    pass
