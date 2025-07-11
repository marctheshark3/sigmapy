"""
Configuration validators for SigmaPy operations

This module provides validation functions for different types of
configuration files used in SigmaPy operations.
"""

from typing import Dict, Any, List
import logging


class ConfigValidator:
    """
    Configuration validation utilities.
    
    This class provides methods to validate configuration files
    for different types of operations.
    """
    
    def __init__(self):
        """Initialize ConfigValidator."""
        self.logger = logging.getLogger(__name__)
    
    @staticmethod
    def validate_address(address: str) -> bool:
        """
        Validate an Ergo address format.
        
        Args:
            address: Address string to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not address or not isinstance(address, str):
            return False
        
        # Basic validation - check length and prefix
        if len(address) < 40:
            return False
        
        # Check if it starts with valid prefix
        if not (address.startswith("9") or address.startswith("3")):
            return False
        
        return True
    
    @staticmethod
    def validate_amount(amount: Any) -> bool:
        """
        Validate an amount value.
        
        Args:
            amount: Amount to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(amount, (int, float)):
            return False
        
        if amount <= 0:
            return False
        
        return True
    
    @staticmethod
    def validate_token_id(token_id: str) -> bool:
        """
        Validate a token ID format.
        
        Args:
            token_id: Token ID to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not token_id or not isinstance(token_id, str):
            return False
        
        # Basic validation - check length (token IDs are 64 character hex strings)
        if len(token_id) != 64:
            return False
        
        # Check if it's a valid hex string
        try:
            int(token_id, 16)
            return True
        except ValueError:
            return False
    
    def __str__(self) -> str:
        """String representation of ConfigValidator."""
        return "ConfigValidator()"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return "ConfigValidator()"