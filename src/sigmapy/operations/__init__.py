"""
High-level operation interfaces for common Ergo blockchain tasks

This module provides simplified interfaces for:
- NFT minting and management with EIP-24 compliance
- Token creation and distribution
- Collection token management
- Complex multi-recipient royalty structures
- Smart contract deployment and interaction (TODO)
- Batch processing operations (TODO)
"""

from .token_manager import TokenManager
from .collection_manager import CollectionManager
from .nft_minter import NFTMinter
from .royalty_manager import RoyaltyManager

# TODO: Implement these
# from .contract_manager import ContractManager
# from .batch_processor import BatchProcessor

__all__ = [
    "TokenManager",
    "CollectionManager",
    "NFTMinter", 
    "RoyaltyManager",
    # "ContractManager", # TODO
    # "BatchProcessor",  # TODO
]