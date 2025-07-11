"""
Practical examples for Ergo blockchain development

This module contains ready-to-use examples for common Ergo operations:
- Simple payment transactions
- Token minting and transfers
- Multi-signature wallets
- Smart contract interactions
- NFT operations
"""

from .simple_payment import SimplePaymentExample
from .advanced_transaction import AdvancedTransactionExample
from .token_operations import TokenOperationsExample
from .nft_examples import NFTExample
from .multisig_example import MultiSigExample

__all__ = [
    "SimplePaymentExample",
    "AdvancedTransactionExample",
    "TokenOperationsExample",
    "NFTExample", 
    "MultiSigExample",
]