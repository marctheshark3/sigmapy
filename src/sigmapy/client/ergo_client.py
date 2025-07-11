"""
ErgoClient - Main high-level interface for Ergo blockchain operations

This class provides a simplified, beginner-friendly interface for all common
Ergo blockchain operations including wallet management, NFT minting, token
operations, and smart contract interactions.
"""

from typing import Dict, List, Optional, Union, Any
import logging
from pathlib import Path

from ..operations import NFTMinter, TokenManager, ContractManager, BatchProcessor
from ..utils import AmountUtils, SerializationUtils, EnvManager
from .wallet_manager import WalletManager
from .network_manager import NetworkManager


class ErgoClient:
    """
    High-level client for Ergo blockchain operations.
    
    This class provides simple, one-line methods for common operations:
    - Wallet management (seed phrase, node connection)
    - NFT minting (single and batch)
    - Token creation and distribution
    - Smart contract deployment
    - Batch processing operations
    
    Examples:
        >>> # Initialize with seed phrase
        >>> client = ErgoClient(seed_phrase="your seed phrase here")
        >>> 
        >>> # Mint an NFT
        >>> nft_id = client.mint_nft(
        ...     name="My First NFT",
        ...     description="A unique digital asset",
        ...     image_url="https://example.com/image.png"
        ... )
        >>> 
        >>> # Distribute tokens to multiple addresses
        >>> client.distribute_tokens(
        ...     token_id="abc123...",
        ...     config_file="distribution.yaml"
        ... )
    """
    
    def __init__(
        self,
        seed_phrase: Optional[str] = None,
        node_url: Optional[str] = None,
        network: Optional[str] = None,
        api_key: Optional[str] = None,
        env_file: Optional[str] = None
    ):
        """
        Initialize the ErgoClient.
        
        Args:
            seed_phrase: Wallet seed phrase for signing transactions (overrides env)
            node_url: Ergo node URL (overrides env, defaults to public nodes)
            network: Network to use ("mainnet" or "testnet") (overrides env)
            api_key: API key for node access (overrides env)
            env_file: Path to .env file (defaults to .env in current directory)
            
        Examples:
            >>> # Initialize with environment variables
            >>> client = ErgoClient()
            >>> 
            >>> # Initialize with explicit parameters
            >>> client = ErgoClient(
            ...     seed_phrase="abandon abandon abandon...",
            ...     node_url="http://localhost:9053",
            ...     network="testnet"
            ... )
            >>> 
            >>> # Initialize with custom .env file
            >>> client = ErgoClient(env_file="custom.env")
        """
        self.logger = logging.getLogger(__name__)
        
        # Initialize environment manager
        self.env_manager = EnvManager(env_file)
        
        # Get configuration from environment or parameters
        config = self._get_config(seed_phrase, node_url, network, api_key)
        
        # Validate security
        security = self.env_manager.validate_security()
        if not security["secure"]:
            for issue in security["issues"]:
                self.logger.error(f"Security issue: {issue}")
            if config["network"] == "mainnet":
                raise ValueError("Security issues detected for mainnet operations")
        
        for warning in security["warnings"]:
            self.logger.warning(f"Security warning: {warning}")
        
        # Initialize managers
        self.wallet_manager = WalletManager(config["seed_phrase"])
        self.network_manager = NetworkManager(
            config["node_url"], 
            config["network"], 
            config["api_key"],
            config["timeout"]
        )
        
        # Initialize operation handlers
        self.nft_minter = NFTMinter(self.wallet_manager, self.network_manager)
        self.token_manager = TokenManager(self.wallet_manager, self.network_manager)
        self.contract_manager = ContractManager(self.wallet_manager, self.network_manager)
        self.batch_processor = BatchProcessor(self.wallet_manager, self.network_manager)
        
        self.logger.info(f"ErgoClient initialized for {config['network']}")
    
    def _get_config(
        self, 
        seed_phrase: Optional[str], 
        node_url: Optional[str], 
        network: Optional[str], 
        api_key: Optional[str]
    ) -> Dict[str, Any]:
        """
        Get configuration from parameters or environment.
        
        Args:
            seed_phrase: Explicit seed phrase parameter
            node_url: Explicit node URL parameter
            network: Explicit network parameter
            api_key: Explicit API key parameter
            
        Returns:
            Dictionary containing final configuration
        """
        return {
            "seed_phrase": seed_phrase or self.env_manager.get_seed_phrase(),
            "node_url": node_url or self.env_manager.get_node_url(),
            "network": network or self.env_manager.get_network(),
            "api_key": api_key or self.env_manager.get_api_key(),
            "timeout": self.env_manager.get_timeout(),
            "demo_mode": self.env_manager.get_demo_mode(),
        }
    
    # Wallet Operations
    def get_balance(self, address: Optional[str] = None) -> Dict[str, Any]:
        """
        Get wallet balance.
        
        Args:
            address: Specific address to check (uses default if None)
            
        Returns:
            Dictionary containing balance information
            
        Examples:
            >>> balance = client.get_balance()
            >>> print(f"ERG Balance: {balance['erg']} ERG")
            >>> print(f"Tokens: {balance['tokens']}")
        """
        return self.wallet_manager.get_balance(address)
    
    def get_addresses(self, count: int = 1) -> List[str]:
        """
        Get wallet addresses.
        
        Args:
            count: Number of addresses to return
            
        Returns:
            List of wallet addresses
            
        Examples:
            >>> addresses = client.get_addresses(5)
            >>> print(f"Primary address: {addresses[0]}")
        """
        return self.wallet_manager.get_addresses(count)
    
    def send_erg(
        self,
        recipient: str,
        amount_erg: float,
        fee_erg: float = 0.001
    ) -> str:
        """
        Send ERG to an address.
        
        Args:
            recipient: Recipient address
            amount_erg: Amount to send in ERG
            fee_erg: Transaction fee in ERG
            
        Returns:
            Transaction ID
            
        Examples:
            >>> tx_id = client.send_erg(
            ...     recipient="9f...",
            ...     amount_erg=1.5
            ... )
            >>> print(f"Transaction sent: {tx_id}")
        """
        return self.wallet_manager.send_erg(recipient, amount_erg, fee_erg)
    
    # NFT Operations
    def mint_nft(
        self,
        name: str,
        description: str,
        image_url: Optional[str] = None,
        traits: Optional[Dict[str, Any]] = None,
        recipient: Optional[str] = None
    ) -> str:
        """
        Mint a single NFT.
        
        Args:
            name: NFT name
            description: NFT description
            image_url: URL to NFT image
            traits: Dictionary of NFT traits/attributes
            recipient: Address to receive NFT (uses default if None)
            
        Returns:
            NFT token ID
            
        Examples:
            >>> nft_id = client.mint_nft(
            ...     name="My First NFT",
            ...     description="A unique digital asset",
            ...     image_url="https://example.com/image.png",
            ...     traits={"rarity": "rare", "color": "blue"}
            ... )
            >>> print(f"NFT minted: {nft_id}")
        """
        return self.nft_minter.mint_single_nft(
            name=name,
            description=description,
            image_url=image_url,
            traits=traits,
            recipient=recipient
        )
    
    def mint_nft_collection(self, config_file: Union[str, Path]) -> List[str]:
        """
        Mint a collection of NFTs from a configuration file.
        
        Args:
            config_file: Path to YAML/JSON configuration file
            
        Returns:
            List of NFT token IDs
            
        Examples:
            >>> nft_ids = client.mint_nft_collection("my_collection.yaml")
            >>> print(f"Minted {len(nft_ids)} NFTs")
        """
        return self.nft_minter.mint_collection(config_file)
    
    # Token Operations
    def create_token(
        self,
        name: str,
        description: str,
        supply: int,
        decimals: int = 0,
        recipient: Optional[str] = None
    ) -> str:
        """
        Create a new token.
        
        Args:
            name: Token name
            description: Token description
            supply: Initial token supply
            decimals: Number of decimal places
            recipient: Address to receive tokens (uses default if None)
            
        Returns:
            Token ID
            
        Examples:
            >>> token_id = client.create_token(
            ...     name="My Token",
            ...     description="A utility token",
            ...     supply=1000000,
            ...     decimals=2
            ... )
            >>> print(f"Token created: {token_id}")
        """
        return self.token_manager.create_token(
            name=name,
            description=description,
            supply=supply,
            decimals=decimals,
            recipient=recipient
        )
    
    def send_tokens(
        self,
        token_id: str,
        recipient: str,
        amount: int,
        fee_erg: float = 0.001
    ) -> str:
        """
        Send tokens to an address.
        
        Args:
            token_id: Token ID to send
            recipient: Recipient address
            amount: Amount of tokens to send
            fee_erg: Transaction fee in ERG
            
        Returns:
            Transaction ID
            
        Examples:
            >>> tx_id = client.send_tokens(
            ...     token_id="abc123...",
            ...     recipient="9f...",
            ...     amount=100
            ... )
            >>> print(f"Tokens sent: {tx_id}")
        """
        return self.token_manager.send_tokens(token_id, recipient, amount, fee_erg)
    
    def distribute_tokens(
        self,
        token_id: str,
        config_file: Union[str, Path]
    ) -> List[str]:
        """
        Distribute tokens to multiple addresses from a configuration file.
        
        Args:
            token_id: Token ID to distribute
            config_file: Path to YAML/JSON configuration file
            
        Returns:
            List of transaction IDs
            
        Examples:
            >>> tx_ids = client.distribute_tokens(
            ...     token_id="abc123...",
            ...     config_file="distribution.yaml"
            ... )
            >>> print(f"Distributed in {len(tx_ids)} transactions")
        """
        return self.token_manager.distribute_tokens(token_id, config_file)
    
    def airdrop_tokens(
        self,
        token_id: str,
        addresses: List[str],
        amounts: List[int]
    ) -> List[str]:
        """
        Airdrop tokens to multiple addresses.
        
        Args:
            token_id: Token ID to airdrop
            addresses: List of recipient addresses
            amounts: List of amounts corresponding to each address
            
        Returns:
            List of transaction IDs
            
        Examples:
            >>> tx_ids = client.airdrop_tokens(
            ...     token_id="abc123...",
            ...     addresses=["9f...", "9g...", "9h..."],
            ...     amounts=[10, 20, 30]
            ... )
            >>> print(f"Airdropped to {len(addresses)} addresses")
        """
        return self.token_manager.airdrop_tokens(token_id, addresses, amounts)
    
    # Smart Contract Operations
    def deploy_contract(
        self,
        contract_code: str,
        parameters: Optional[Dict[str, Any]] = None,
        initial_funds_erg: float = 0.01
    ) -> str:
        """
        Deploy a smart contract.
        
        Args:
            contract_code: ErgoScript contract code
            parameters: Contract parameters
            initial_funds_erg: Initial ERG to fund the contract
            
        Returns:
            Contract address
            
        Examples:
            >>> contract_address = client.deploy_contract(
            ...     contract_code="{ sigmaProp(true) }",
            ...     initial_funds_erg=1.0
            ... )
            >>> print(f"Contract deployed: {contract_address}")
        """
        return self.contract_manager.deploy_contract(
            contract_code, parameters, initial_funds_erg
        )
    
    def interact_with_contract(
        self,
        contract_address: str,
        method: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Interact with a deployed smart contract.
        
        Args:
            contract_address: Address of the deployed contract
            method: Method to call on the contract
            parameters: Method parameters
            
        Returns:
            Transaction ID
            
        Examples:
            >>> tx_id = client.interact_with_contract(
            ...     contract_address="9f...",
            ...     method="withdraw",
            ...     parameters={"amount": 1000}
            ... )
            >>> print(f"Contract interaction: {tx_id}")
        """
        return self.contract_manager.interact_with_contract(
            contract_address, method, parameters
        )
    
    # Batch Operations
    def batch_operation(self, config_file: Union[str, Path]) -> Dict[str, Any]:
        """
        Execute a batch operation from a configuration file.
        
        Args:
            config_file: Path to YAML/JSON configuration file
            
        Returns:
            Dictionary containing operation results
            
        Examples:
            >>> results = client.batch_operation("batch_config.yaml")
            >>> print(f"Completed {results['successful']} operations")
        """
        return self.batch_processor.execute_batch(config_file)
    
    # Utility Methods
    def get_network_info(self) -> Dict[str, Any]:
        """
        Get network information.
        
        Returns:
            Dictionary containing network details
            
        Examples:
            >>> info = client.get_network_info()
            >>> print(f"Network: {info['network']}")
            >>> print(f"Block height: {info['height']}")
        """
        return self.network_manager.get_network_info()
    
    def get_transaction_status(self, tx_id: str) -> Dict[str, Any]:
        """
        Get transaction status.
        
        Args:
            tx_id: Transaction ID to check
            
        Returns:
            Dictionary containing transaction status
            
        Examples:
            >>> status = client.get_transaction_status("abc123...")
            >>> print(f"Confirmations: {status['confirmations']}")
        """
        return self.network_manager.get_transaction_status(tx_id)
    
    def wait_for_confirmation(
        self,
        tx_id: str,
        timeout_seconds: int = 300
    ) -> Dict[str, Any]:
        """
        Wait for transaction confirmation.
        
        Args:
            tx_id: Transaction ID to wait for
            timeout_seconds: Maximum time to wait
            
        Returns:
            Dictionary containing final transaction status
            
        Examples:
            >>> status = client.wait_for_confirmation("abc123...")
            >>> print(f"Transaction confirmed in block {status['block_height']}")
        """
        return self.network_manager.wait_for_confirmation(tx_id, timeout_seconds)
    
    # Helper Methods
    def erg_to_nanoerg(self, erg_amount: float) -> int:
        """Convert ERG to nanoERG."""
        return AmountUtils.erg_to_nanoerg(erg_amount)
    
    def nanoerg_to_erg(self, nanoerg_amount: int) -> float:
        """Convert nanoERG to ERG."""
        return float(AmountUtils.nanoerg_to_erg(nanoerg_amount))
    
    def validate_address(self, address: str) -> bool:
        """Validate an Ergo address."""
        return self.network_manager.validate_address(address)
    
    def __str__(self) -> str:
        """String representation of the client."""
        return f"ErgoClient(network={self.network_manager.network})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return (
            f"ErgoClient("
            f"network={self.network_manager.network}, "
            f"has_wallet={self.wallet_manager.has_wallet()}"
            f")"
        )