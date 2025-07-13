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

# Operation managers (only what exists)
from .operations import TokenManager
# from .operations import NFTMinter, BatchProcessor  # TODO: Implement these
# from .config import ConfigParser  # TODO: Implement this

# Essential utilities only
from .utils import AmountUtils, EnvManager

__all__ = [
    # High-level API
    "ErgoClient",
    
    # Operation managers  
    "TokenManager",
    
    # Configuration
    "ConfigParser",
    
    # Utilities
    "AmountUtils",
    "EnvManager",
]