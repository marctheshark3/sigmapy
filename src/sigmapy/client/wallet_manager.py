"""
WalletManager - Wallet operations and management

This class handles wallet-related operations including:
- Seed phrase management
- Address generation
- Balance checking
- Transaction signing
- UTXO management
"""

from typing import Dict, List, Optional, Any, Union
import logging
from decimal import Decimal

from ..utils import AmountUtils

try:
    import ergo_lib_python as ergo
    ERGO_LIB_AVAILABLE = True
except ImportError:
    ERGO_LIB_AVAILABLE = False
    ergo = None


class WalletManager:
    """
    Manages wallet operations and provides a unified interface for
    different wallet connection methods (seed phrase, node, future Nautilus).
    """
    
    def __init__(self, seed_phrase: Optional[str] = None, network: str = "mainnet"):
        """
        Initialize the WalletManager.
        
        Args:
            seed_phrase: Wallet seed phrase for signing transactions
            network: Network type ("mainnet" or "testnet")
        """
        self.logger = logging.getLogger(__name__)
        self.seed_phrase = seed_phrase
        self.network = network
        self.addresses = []
        self.cached_balances = {}
        self.secret_key = None
        self.wallet = None
        
        # Set network type
        if ERGO_LIB_AVAILABLE and ergo:
            self.network_type = ergo.NetworkType.Mainnet if network == "mainnet" else ergo.NetworkType.Testnet
        else:
            self.network_type = None
            self.logger.warning("ergo-lib-python not installed - using demo mode")
        
        # Initialize wallet connection
        if seed_phrase:
            self._initialize_wallet_from_seed(seed_phrase)
    
    def _initialize_wallet_from_seed(self, seed_phrase: str) -> None:
        """Initialize wallet from seed phrase."""
        self.logger.info("Initializing wallet from seed phrase")
        
        if not ERGO_LIB_AVAILABLE:
            self.logger.warning("ergo-lib-python not available. Using demo mode.")
            # Demo addresses for testing
            self.addresses = [
                "9fRusAarL1KkrWQVsxSRVYnvWzD4dWoLLxbYk3eWBV3jD3qvr3W",
                "9gQqZyxyjAptMbfW1Gydm3qaap11zd6X9DrABTbMBRJLjZhQRCA",
                "9h8UVJjdUYbNLuSqzZCqKNs2mxjVGYB9JwP4vVtNqmR3sKdxYyZ"
            ]
            return
        
        try:
            # Convert seed phrase to secret key
            mnemonic = ergo.Mnemonic.from_phrase(seed_phrase)
            seed = mnemonic.to_seed("")
            self.secret_key = ergo.SecretKey.derive_master(seed)
            
            # Generate first address
            address = self._derive_address(0)
            self.addresses = [str(address)]
            
            self.logger.info(f"Wallet initialized successfully for network: {self.network}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize wallet: {e}")
            raise ValueError(f"Invalid seed phrase or initialization error: {e}")
    
    def _derive_address(self, index: int) -> str:
        """Derive address at given index."""
        if not ERGO_LIB_AVAILABLE or not self.secret_key:
            return f"9demo_address_{index}"
        
        # Derive child key for the given index
        child_key = self.secret_key.derive_child(index)
        public_key = child_key.get_public_key()
        address = ergo.Address.p2pk(public_key, self.network_type)
        return str(address)
    
    def has_wallet(self) -> bool:
        """Check if wallet is initialized."""
        return self.seed_phrase is not None
    
    def get_addresses(self, count: int = 1) -> List[str]:
        """
        Get wallet addresses.
        
        Args:
            count: Number of addresses to return
            
        Returns:
            List of wallet addresses
        """
        if not self.has_wallet():
            raise ValueError("No wallet initialized")
        
        # Generate additional addresses if needed
        while len(self.addresses) < count:
            index = len(self.addresses)
            new_address = self._derive_address(index)
            self.addresses.append(new_address)
        
        return self.addresses[:count]
    
    def get_primary_address(self) -> str:
        """Get the primary wallet address."""
        addresses = self.get_addresses(1)
        return addresses[0]
    
    def get_balance(self, address: Optional[str] = None) -> Dict[str, Any]:
        """
        Get balance for an address.
        
        Args:
            address: Address to check (uses primary if None)
            
        Returns:
            Dictionary containing balance information
        """
        if address is None:
            address = self.get_primary_address()
        
        if not ERGO_LIB_AVAILABLE:
            # Demo mode - return simulated balance
            return {
                "address": address,
                "erg": 10.0,
                "nanoerg": 10000000000,
                "tokens": [
                    {"id": "demo_token_1", "amount": 100, "name": "Demo Token"},
                    {"id": "demo_token_2", "amount": 50, "name": "Another Token"}
                ],
                "utxos": 5
            }
        
        # This would be implemented with actual node calls in NetworkManager
        # For now, return empty balance as NetworkManager will handle actual queries
        return {
            "address": address,
            "erg": 0.0,
            "nanoerg": 0,
            "tokens": [],
            "utxos": 0
        }
    
    def get_utxos(self, address: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get UTXOs for an address.
        
        Args:
            address: Address to check (uses primary if None)
            
        Returns:
            List of UTXO dictionaries
        """
        if address is None:
            address = self.get_primary_address()
        
        if not ERGO_LIB_AVAILABLE:
            # Demo mode - return simulated UTXOs
            return [
                {
                    "box_id": "demo_box_1",
                    "value": 5000000000,
                    "address": address,
                    "tokens": []
                },
                {
                    "box_id": "demo_box_2",
                    "value": 3000000000,
                    "address": address,
                    "tokens": [{"id": "demo_token_1", "amount": 100}]
                }
            ]
        
        # This would be implemented with actual node calls in NetworkManager
        return []
    
    def sign_transaction(self, unsigned_tx: Any) -> Any:
        """
        Sign a transaction.
        
        Args:
            unsigned_tx: Unsigned transaction to sign
            
        Returns:
            Signed transaction
        """
        if not self.has_wallet():
            raise ValueError("No wallet available for signing")
        
        if not ERGO_LIB_AVAILABLE:
            self.logger.warning("ergo-lib-python not available. Cannot sign transaction.")
            return unsigned_tx
        
        if not self.secret_key:
            raise ValueError("No secret key available for signing")
        
        try:
            # Create wallet from secret key
            wallet = ergo.Wallet.from_secrets([self.secret_key])
            
            # Sign the transaction
            signed_tx = wallet.sign_transaction(unsigned_tx)
            return signed_tx
            
        except Exception as e:
            self.logger.error(f"Failed to sign transaction: {e}")
            raise ValueError(f"Transaction signing failed: {e}")
    
    def create_transaction_builder(self) -> Any:
        """
        Create a transaction builder instance.
        
        Returns:
            Transaction builder instance
        """
        if not ERGO_LIB_AVAILABLE:
            raise NotImplementedError("Transaction builder not available in demo mode")
        
        return ergo.TxBuilder()
    
    def validate_seed_phrase(self, seed_phrase: str) -> bool:
        """
        Validate a seed phrase.
        
        Args:
            seed_phrase: Seed phrase to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not seed_phrase:
            return False
        
        # Basic validation - check word count
        words = seed_phrase.split()
        if len(words) not in [12, 15, 18, 21, 24]:
            return False
        
        if not ERGO_LIB_AVAILABLE:
            # Demo mode - basic validation
            return len(words) >= 12
        
        try:
            # Try to create mnemonic from phrase
            mnemonic = ergo.Mnemonic.from_phrase(seed_phrase)
            return True
        except:
            return False
    
    def validate_address(self, address: str) -> bool:
        """
        Validate an Ergo address.
        
        Args:
            address: Address to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not address:
            return False
        
        if not ERGO_LIB_AVAILABLE:
            # Demo mode - basic validation
            return address.startswith("9") and len(address) > 30
        
        try:
            # Try to parse address
            ergo.Address.from_base58(address)
            return True
        except:
            return False
    
    def get_network_type(self) -> str:
        """Get the current network type."""
        return self.network
    
    def is_demo_mode(self) -> bool:
        """Check if running in demo mode."""
        return not ERGO_LIB_AVAILABLE
    
    def __str__(self) -> str:
        """String representation of the wallet manager."""
        return f"WalletManager(has_wallet={self.has_wallet()}, network={self.network})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return (
            f"WalletManager("
            f"has_wallet={self.has_wallet()}, "
            f"network={self.network}, "
            f"addresses={len(self.addresses)}, "
            f"demo_mode={self.is_demo_mode()}"
            f")"
        )