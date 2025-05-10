"""
Code quality and documentation analysis
"""

from code_chunker import CodeChunker
from typing import Dict, List
import re

def analyze_documentation(result) -> Dict:
    """Analyze code documentation quality
    
    Args:
        result: Parse result
        
    Returns:
        Dictionary of documentation statistics
    """
    stats = {
        'total_chunks': len(result.chunks),
        'documented_chunks': 0,
        'functions_with_docstrings': 0,
        'classes_with_docstrings': 0,
        'methods_with_docstrings': 0,
        'type_annotated_functions': 0,
        'complex_functions': 0,  # Functions with high cyclomatic complexity
        'long_functions': 0,     # Functions over 50 lines
        'documentation_coverage': 0.0,
    }
    
    for chunk in result.chunks:
        # Check for docstrings
        has_docstring = False
        code_lines = chunk.code.split('\n')
        
        # Simple docstring detection
        for i, line in enumerate(code_lines):
            if '"""' in line or "'''" in line:
                has_docstring = True
                break
        
        if has_docstring:
            stats['documented_chunks'] += 1
            
            if chunk.type.value == 'function':
                stats['functions_with_docstrings'] += 1
            elif chunk.type.value == 'class':
                stats['classes_with_docstrings'] += 1
            elif chunk.type.value == 'method':
                stats['methods_with_docstrings'] += 1
        
        # Check type annotations (Python)
        if result.language == 'python' and chunk.type.value in ['function', 'method']:
            if '->' in chunk.code or ': ' in chunk.code:
                stats['type_annotated_functions'] += 1
        
        # Check function complexity
        if chunk.type.value in ['function', 'method']:
            # Simple complexity estimation
            if_count = chunk.code.count('if ')
            for_count = chunk.code.count('for ')
            while_count = chunk.code.count('while ')
            
            complexity = if_count + for_count + while_count
            if complexity > 5:
                stats['complex_functions'] += 1
            
            # Check function length
            if len(code_lines) > 50:
                stats['long_functions'] += 1
    
    # Calculate documentation coverage
    if stats['total_chunks'] > 0:
        stats['documentation_coverage'] = (
            stats['documented_chunks'] / stats['total_chunks']
        ) * 100
    
    return stats

def generate_quality_report(file_path: str):
    """Generate code quality report
    
    Args:
        file_path: Path to the file to analyze
        
    Returns:
        Quality report string
    """
    chunker = CodeChunker()
    result = chunker.parse_file(file_path)
    
    # Basic statistics
    stats = analyze_documentation(result)
    
    # Generate report
    report = f"""
Code Quality Report
==================

File: {file_path}
Language: {result.language}

Overview
--------
Total code chunks: {stats['total_chunks']}
Documentation coverage: {stats['documentation_coverage']:.1f}%

Documentation
-------------
Functions with docstrings: {stats['functions_with_docstrings']}
Classes with docstrings: {stats['classes_with_docstrings']}
Methods with docstrings: {stats['methods_with_docstrings']}

Code Quality Metrics
-------------------
Type-annotated functions: {stats['type_annotated_functions']}
Complex functions (high cyclomatic complexity): {stats['complex_functions']}
Long functions (>50 lines): {stats['long_functions']}

Recommendations
--------------
"""
    
    recommendations = []
    
    if stats['documentation_coverage'] < 80:
        recommendations.append(
            f"- Improve documentation coverage (currently {stats['documentation_coverage']:.1f}%)"
        )
    
    if stats['complex_functions'] > 0:
        recommendations.append(
            f"- Refactor {stats['complex_functions']} complex functions"
        )
    
    if stats['long_functions'] > 0:
        recommendations.append(
            f"- Split {stats['long_functions']} long functions into smaller ones"
        )
    
    if result.language == 'python' and stats['type_annotated_functions'] < stats['total_chunks'] / 2:
        recommendations.append(
            "- Add type annotations to more functions"
        )
    
    if recommendations:
        report += '\n'.join(recommendations)
    else:
        report += "Great job! The code quality looks good."
    
    return report

if __name__ == '__main__':
    # Test quality analysis
    import sys
    if len(sys.argv) > 1:
        report = generate_quality_report(sys.argv[1])
        print(report)
    else:
        print("Usage: python quality_analysis.py <file_path>") 