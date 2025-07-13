"""
Address utilities for Ergo blockchain operations.

This module provides utility functions for address validation,
formatting, and network detection.
"""

from typing import Optional
import re

try:
    import ergo_lib_python as ergo
    ERGO_LIB_AVAILABLE = True
except ImportError:
    ERGO_LIB_AVAILABLE = False
    ergo = None


class AddressUtils:
    """Utilities for Ergo address operations."""
    
    @staticmethod
    def validate_address(address: str) -> bool:
        """
        Validate an Ergo address.
        
        Args:
            address: Address to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not address or not isinstance(address, str):
            return False
        
        # Basic length check
        if len(address) < 30:
            return False
        
        # Check if starts with valid network prefix
        if not (address.startswith('9') or address.startswith('3')):
            return False
        
        if ERGO_LIB_AVAILABLE:
            try:
                ergo.Address.from_base58(address)
                return True
            except:
                return False
        else:
            # Basic validation for demo mode
            # Check address format with regex
            pattern = r'^[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{40,60}$'
            return bool(re.match(pattern, address))
    
    @staticmethod
    def get_network_type(address: str) -> Optional[str]:
        """
        Determine network type from address.
        
        Args:
            address: Address to check
            
        Returns:
            'mainnet' or 'testnet' or None if invalid
        """
        if not AddressUtils.validate_address(address):
            return None
        
        if address.startswith('9'):
            return 'mainnet'
        elif address.startswith('3'):
            return 'testnet'
        else:
            return None
    
    @staticmethod
    def is_mainnet_address(address: str) -> bool:
        """Check if address is for mainnet."""
        return AddressUtils.get_network_type(address) == 'mainnet'
    
    @staticmethod
    def is_testnet_address(address: str) -> bool:
        """Check if address is for testnet."""
        return AddressUtils.get_network_type(address) == 'testnet'
    
    @staticmethod
    def format_address(address: str, short: bool = False) -> str:
        """
        Format address for display.
        
        Args:
            address: Address to format
            short: If True, show only first/last characters
            
        Returns:
            Formatted address string
        """
        if not AddressUtils.validate_address(address):
            return "Invalid Address"
        
        if short and len(address) > 20:
            return f"{address[:6]}...{address[-6:]}"
        
        return address
    
    @staticmethod
    def batch_validate_addresses(addresses: list) -> dict:
        """
        Validate multiple addresses.
        
        Args:
            addresses: List of addresses to validate
            
        Returns:
            Dict with validation results
        """
        results = {
            'valid': [],
            'invalid': [],
            'mainnet': [],
            'testnet': []
        }
        
        for addr in addresses:
            if AddressUtils.validate_address(addr):
                results['valid'].append(addr)
                
                network = AddressUtils.get_network_type(addr)
                if network == 'mainnet':
                    results['mainnet'].append(addr)
                elif network == 'testnet':
                    results['testnet'].append(addr)
            else:
                results['invalid'].append(addr)
        
        return results