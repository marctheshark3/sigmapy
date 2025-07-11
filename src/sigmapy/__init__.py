"""
SigmaPy - Beginner-friendly tutorials and examples for Ergo blockchain development

This package provides comprehensive tutorials and practical examples for working
with the Ergo blockchain using Python. It serves as a learning resource and
reference implementation for common Ergo development patterns.

Key Features:
- Step-by-step tutorials for Ergo blockchain concepts
- Practical examples with real-world use cases
- Beginner-friendly abstractions over ergo-lib-python
- High-level APIs for common operations
- Configuration-driven batch operations
- Comprehensive documentation and code comments
"""

__version__ = "0.1.0"
__author__ = "Ergo Community"
__email__ = "community@ergoplatform.org"

# High-level API - Main entry point
from .client import ErgoClient

# Operation managers
from .operations import NFTMinter, TokenManager, BatchProcessor
from .config import ConfigParser

# Tutorials and examples
from .tutorials import *
from .examples import *
from .utils import *

__all__ = [
    # High-level API
    "ErgoClient",
    
    # Operation managers
    "NFTMinter",
    "TokenManager", 
    "BatchProcessor",
    
    # Configuration
    "ConfigParser",
    
    # Tutorials and examples
    "tutorials",
    "examples", 
    "utils",
]