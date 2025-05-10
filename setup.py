"""
Setup script for code-chunker
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read version
version_file = Path(__file__).parent / 'code_chunker' / '__version__.py'
version_data = {}
exec(version_file.read_text(), version_data)
version = version_data['__version__']

# Read README
readme_file = Path(__file__).parent / 'README.md'
long_description = readme_file.read_text(encoding='utf-8')

setup(
    name='code-chunker',
    version=version,
    author='Jim Fang',
    author_email='jimthebeacon@gmail.com',
    description='A pragmatic multi-language code parser optimized for LLM applications',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/jimthebeacon/code-chunker',
    project_urls={
        'Bug Tracker': 'https://github.com/jimthebeacon/code-chunker/issues',
        'Documentation': 'https://github.com/jimthebeacon/code-chunker#readme',
        'Source Code': 'https://github.com/jimthebeacon/code-chunker',
    },
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Linguistic',
        'Topic :: Software Development :: Code Generators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.11',
    install_requires=[
        # No external dependencies to keep it lightweight
    ],
    extras_require={
        'dev': [
            'pytest>=7.0',
            'pytest-cov>=4.0',
            'black>=23.0',
            'mypy>=1.0',
            'ruff>=0.1.0',
        ],
    },
    keywords=[
        'code parser',
        'code analyzer',
        'multi-language parser',
        'llm',
        'rag',
        'code chunking',
        'ast parser',
        'python parser',
        'javascript parser',
        'typescript parser',
        'solidity parser',
    ],
)
