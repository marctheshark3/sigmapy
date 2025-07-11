"""
Template management for SigmaPy configurations

This module provides templates for common configuration patterns
and utilities for creating and managing configuration templates.
"""

from typing import Dict, Any, List
import logging


class TemplateManager:
    """
    Template management utilities.
    
    This class provides methods to generate and manage configuration
    templates for common SigmaPy operations.
    """
    
    def __init__(self):
        """Initialize TemplateManager."""
        self.logger = logging.getLogger(__name__)
    
    @staticmethod
    def get_nft_collection_template() -> Dict[str, Any]:
        """
        Get NFT collection configuration template.
        
        Returns:
            Dictionary containing NFT collection template
        """
        return {
            "collection": {
                "name": "My NFT Collection",
                "description": "A unique collection of digital assets",
                "creator": "Artist Name",
                "royalty": 0.05,
                "website": "https://example.com",
                "social": {
                    "twitter": "@artist",
                    "discord": "https://discord.gg/collection"
                }
            },
            "nfts": [
                {
                    "name": "NFT #1",
                    "description": "First NFT in the collection",
                    "image": "https://example.com/image1.png",
                    "traits": {
                        "background": "blue",
                        "rarity": "common",
                        "attribute1": "value1"
                    }
                },
                {
                    "name": "NFT #2",
                    "description": "Second NFT in the collection",
                    "image": "https://example.com/image2.png",
                    "traits": {
                        "background": "red",
                        "rarity": "rare",
                        "attribute1": "value2"
                    }
                }
            ]
        }
    
    @staticmethod
    def get_token_distribution_template() -> Dict[str, Any]:
        """
        Get token distribution configuration template.
        
        Returns:
            Dictionary containing token distribution template
        """
        return {
            "distribution": {
                "token_id": "your_token_id_here",
                "batch_size": 50,
                "fee_per_tx": 0.001
            },
            "recipients": [
                {
                    "address": "9f...",
                    "amount": 100,
                    "note": "Recipient 1"
                },
                {
                    "address": "9g...",
                    "amount": 200,
                    "note": "Recipient 2"
                }
            ]
        }
    
    @staticmethod
    def get_token_creation_template() -> Dict[str, Any]:
        """
        Get token creation configuration template.
        
        Returns:
            Dictionary containing token creation template
        """
        return {
            "tokens": [
                {
                    "name": "My Token",
                    "description": "A utility token",
                    "supply": 1000000,
                    "decimals": 0
                },
                {
                    "name": "Another Token",
                    "description": "Another utility token",
                    "supply": 500000,
                    "decimals": 2
                }
            ]
        }
    
    def __str__(self) -> str:
        """String representation of TemplateManager."""
        return "TemplateManager()"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return "TemplateManager()"