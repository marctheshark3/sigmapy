"""
SigmaPy - Beginner-friendly tutorials and examples for Ergo blockchain development

This package provides comprehensive tutorials and practical examples for working
with the Ergo blockchain using Python. It serves as a learning resource and
reference implementation for common Ergo development patterns.

Key Features:
- Step-by-step tutorials for Ergo blockchain concepts
- Practical examples with real-world use cases
- Beginner-friendly abstractions over ergo-lib-python
- Comprehensive documentation and code comments
"""

__version__ = "0.1.0"
__author__ = "Ergo Community"
__email__ = "community@ergoplatform.org"

from .tutorials import *
from .examples import *
from .utils import *

__all__ = [
    "tutorials",
    "examples", 
    "utils",
]