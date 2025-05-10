"""
Error recovery mechanisms for code-chunker
"""

from typing import List, Optional
from .models import CodeChunk, ChunkType

class ErrorRecovery:
    """Error recovery mechanism"""
    
    @staticmethod
    def attempt_recovery(code: str, error_position: int, language: str) -> Optional[List[CodeChunk]]:
        """Attempt to recover from parsing errors
        
        Args:
            code: The code string that caused the error
            error_position: The position where the error occurred
            language: The programming language
            
        Returns:
            Optional list of partially parsed code chunks
        """
        # Find nearest syntax boundaries
        lines = code.split('\n')
        error_line = code[:error_position].count('\n')
        
        # Try parsing from before and after the error
        safe_start = max(0, error_line - 5)
        safe_end = min(len(lines), error_line + 5)
        
        partial_code = '\n'.join(lines[safe_start:safe_end])
        
        # Return partial parsing results
        return [
            CodeChunk(
                type=ChunkType.UNKNOWN,
                name=f"partial_block_{safe_start}_{safe_end}",
                code=partial_code,
                start_line=safe_start,
                end_line=safe_end,
                language=language,
                confidence=0.5,
                metadata={'error_recovery': True}
            )
        ]
    
    @staticmethod
    def fuzzy_boundary_detection(code: str, language: str) -> List[int]:
        """Detect code boundaries using fuzzy matching
        
        Args:
            code: The code string to analyze
            language: The programming language
            
        Returns:
            List of line numbers where boundaries are detected
        """
        boundaries = []
        lines = code.split('\n')
        
        # Detect boundaries based on indentation changes
        prev_indent = 0
        for i, line in enumerate(lines):
            if line.strip():
                current_indent = len(line) - len(line.lstrip())
                if current_indent < prev_indent:
                    boundaries.append(i)
                prev_indent = current_indent
        
        return boundaries 