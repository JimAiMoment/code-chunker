"""Base exception classes"""


class BaseError(Exception):
    """Base exception class"""
    pass


class LanguageNotSupportedError(BaseError):
    """Exception for unsupported language"""
    pass


class ParserError(BaseError):
    """Exception for parsing errors"""
    pass


class FileProcessingError(BaseError):
    """Exception for file processing errors"""
    pass
