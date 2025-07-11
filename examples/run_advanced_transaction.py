#!/usr/bin/env python3
"""
Standalone script to run the advanced transaction example.

This script demonstrates how to use the AdvancedTransactionExample
from the sigmapy library to create complex transactions with:
- Multiple outputs
- Custom register data
- Context extensions
- Proper serialization

Usage:
    python run_advanced_transaction.py
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sigmapy.examples import AdvancedTransactionExample


def main():
    """Run the advanced transaction example."""
    print("🚀 Running Advanced Transaction Example")
    print("=" * 60)
    print()
    
    # Create and run the example
    example = AdvancedTransactionExample()
    example.run_complete_example()
    
    print("\n" + "=" * 60)
    print("Example completed! Check the output above for details.")
    
    # Additional information
    print("\n📚 What you learned:")
    print("- How to create multiple outputs in a single transaction")
    print("- How to serialize data for ErgoBox registers")
    print("- How to use context extensions for metadata")
    print("- How to sign complex transactions")
    print("- Best practices for handling complex data structures")
    
    print("\n🔧 Next steps:")
    print("- Try modifying the register data types and values")
    print("- Experiment with different context extension structures")
    print("- Add token transfers to the outputs")
    print("- Connect to a real Ergo node for actual transactions")


if __name__ == "__main__":
    main()