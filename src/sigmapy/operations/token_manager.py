"""
TokenManager - Simplified token operations

This class provides easy-to-use methods for:
- Token creation
- Token distribution and transfers
- Batch token operations
- Airdrop functionality
"""

from typing import Dict, List, Optional, Any, Union
import logging
from pathlib import Path
import math

from ..utils import AmountUtils, SerializationUtils
from ..config import ConfigParser


class TokenManager:
    """
    Simplified token management operations.
    
    This class provides beginner-friendly methods for creating and
    managing tokens with automatic batch processing and optimization.
    """
    
    def __init__(self, wallet_manager, network_manager):
        """
        Initialize TokenManager.
        
        Args:
            wallet_manager: WalletManager instance for signing
            network_manager: NetworkManager instance for broadcasting
        """
        self.wallet_manager = wallet_manager
        self.network_manager = network_manager
        self.logger = logging.getLogger(__name__)
    
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
            >>> token_id = manager.create_token(
            ...     name="My Token",
            ...     description="A utility token",
            ...     supply=1000000,
            ...     decimals=2
            ... )
        """
        self.logger.info(f"Creating token: {name} with supply {supply}")
        
        # Get recipient address
        if recipient is None:
            recipient = self.wallet_manager.get_primary_address()
        
        # Build token creation transaction
        tx_data = self._build_token_creation_transaction(
            name, description, supply, decimals, recipient
        )
        
        # Sign and broadcast
        signed_tx = self.wallet_manager.sign_transaction(tx_data)
        tx_id = self.network_manager.broadcast_transaction(signed_tx)
        
        self.logger.info(f"Token created successfully. Transaction ID: {tx_id}")
        return tx_id
    
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
            >>> tx_id = manager.send_tokens(
            ...     token_id="abc123...",
            ...     recipient="9f...",
            ...     amount=100
            ... )
        """
        self.logger.info(f"Sending {amount} tokens ({token_id}) to {recipient}")
        
        return self.wallet_manager.send_tokens(
            token_id=token_id,
            recipient=recipient,
            amount=amount,
            fee_erg=fee_erg
        )
    
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
            
        Config file format:
            distribution:
              token_id: "abc123..."  # Optional, can be overridden
              batch_size: 50  # Optional, default 50
              fee_per_tx: 0.001  # Optional, default 0.001
              
            recipients:
              - address: "9f..."
                amount: 10
              - address: "9g..."
                amount: 20
              # ... up to 100+ recipients
        """
        self.logger.info(f"Distributing tokens from {config_file}")
        
        # Parse configuration
        config = ConfigParser.parse_file(config_file)
        
        # Validate configuration
        self._validate_distribution_config(config)
        
        # Get distribution parameters
        distribution_config = config.get("distribution", {})
        recipients = config.get("recipients", [])
        
        # Use token_id from parameter or config
        config_token_id = distribution_config.get("token_id")
        if config_token_id and config_token_id != token_id:
            self.logger.warning(f"Token ID mismatch: using parameter {token_id}")
        
        batch_size = distribution_config.get("batch_size", 50)
        fee_per_tx = distribution_config.get("fee_per_tx", 0.001)
        
        # Process in batches
        transaction_ids = []
        total_recipients = len(recipients)
        
        for i in range(0, total_recipients, batch_size):
            batch = recipients[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = math.ceil(total_recipients / batch_size)
            
            self.logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} recipients)")
            
            try:
                tx_id = self._process_token_batch(token_id, batch, fee_per_tx)
                transaction_ids.append(tx_id)
                
            except Exception as e:
                self.logger.error(f"Failed to process batch {batch_num}: {e}")
                continue
        
        self.logger.info(f"Token distribution completed. {len(transaction_ids)} transactions sent")
        return transaction_ids
    
    def airdrop_tokens(
        self,
        token_id: str,
        addresses: List[str],
        amounts: List[int],
        batch_size: int = 50,
        fee_per_tx: float = 0.001
    ) -> List[str]:
        """
        Airdrop tokens to multiple addresses.
        
        Args:
            token_id: Token ID to airdrop
            addresses: List of recipient addresses
            amounts: List of amounts corresponding to each address
            batch_size: Number of recipients per transaction
            fee_per_tx: Transaction fee per batch
            
        Returns:
            List of transaction IDs
            
        Examples:
            >>> tx_ids = manager.airdrop_tokens(
            ...     token_id="abc123...",
            ...     addresses=["9f...", "9g...", "9h..."],
            ...     amounts=[10, 20, 30]
            ... )
        """
        if len(addresses) != len(amounts):
            raise ValueError("Addresses and amounts lists must have the same length")
        
        self.logger.info(f"Airdropping tokens to {len(addresses)} addresses")
        
        # Create recipient list
        recipients = [
            {"address": addr, "amount": amt}
            for addr, amt in zip(addresses, amounts)
        ]
        
        # Process in batches
        transaction_ids = []
        total_recipients = len(recipients)
        
        for i in range(0, total_recipients, batch_size):
            batch = recipients[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = math.ceil(total_recipients / batch_size)
            
            self.logger.info(f"Processing airdrop batch {batch_num}/{total_batches} ({len(batch)} recipients)")
            
            try:
                tx_id = self._process_token_batch(token_id, batch, fee_per_tx)
                transaction_ids.append(tx_id)
                
            except Exception as e:
                self.logger.error(f"Failed to process airdrop batch {batch_num}: {e}")
                continue
        
        self.logger.info(f"Airdrop completed. {len(transaction_ids)} transactions sent")
        return transaction_ids
    
    def batch_create_tokens(
        self,
        config_file: Union[str, Path]
    ) -> List[str]:
        """
        Create multiple tokens from a configuration file.
        
        Args:
            config_file: Path to YAML/JSON configuration file
            
        Returns:
            List of token IDs
            
        Config file format:
            tokens:
              - name: "Token A"
                description: "First token"
                supply: 1000000
                decimals: 0
              - name: "Token B"
                description: "Second token"
                supply: 500000
                decimals: 2
              # ... more tokens
        """
        self.logger.info(f"Creating tokens from {config_file}")
        
        # Parse configuration
        config = ConfigParser.parse_file(config_file)
        
        # Validate configuration
        if "tokens" not in config:
            raise ValueError("Configuration must contain 'tokens' section")
        
        tokens = config["tokens"]
        if not isinstance(tokens, list) or len(tokens) == 0:
            raise ValueError("'tokens' must be a non-empty list")
        
        # Create each token
        token_ids = []
        for i, token_config in enumerate(tokens):
            try:
                self.logger.info(f"Creating token {i+1}/{len(tokens)}: {token_config.get('name', 'Unnamed')}")
                
                token_id = self.create_token(
                    name=token_config.get("name", f"Token {i+1}"),
                    description=token_config.get("description", ""),
                    supply=token_config.get("supply", 1000000),
                    decimals=token_config.get("decimals", 0)
                )
                
                token_ids.append(token_id)
                
            except Exception as e:
                self.logger.error(f"Failed to create token {i+1}: {e}")
                continue
        
        self.logger.info(f"Batch token creation completed. Created {len(token_ids)} tokens")
        return token_ids
    
    def _build_token_creation_transaction(
        self,
        name: str,
        description: str,
        supply: int,
        decimals: int,
        recipient: str
    ) -> Dict[str, Any]:
        """Build token creation transaction."""
        
        # Create token metadata registers
        registers = {
            "R4": SerializationUtils.serialize_for_register("R4", name, "String"),
            "R5": SerializationUtils.serialize_for_register("R5", description, "String"),
            "R6": SerializationUtils.serialize_for_register("R6", decimals, "Int"),
            "R7": SerializationUtils.serialize_for_register("R7", supply, "Long")
        }
        
        # Create token output
        token_output = {
            "recipient": recipient,
            "value": AmountUtils.erg_to_nanoerg(0.001),  # Minimum box value
            "tokens": [
                {
                    "id": "TOKEN_ID",  # This would be generated
                    "amount": supply
                }
            ],
            "registers": registers
        }
        
        # Build transaction
        transaction = self.wallet_manager.create_transaction(
            outputs=[token_output],
            fee_erg=0.001
        )
        
        return transaction
    
    def _process_token_batch(
        self,
        token_id: str,
        recipients: List[Dict[str, Any]],
        fee_erg: float
    ) -> str:
        """Process a batch of token recipients."""
        
        # Create outputs for each recipient
        outputs = []
        for recipient in recipients:
            output = {
                "recipient": recipient["address"],
                "value": AmountUtils.erg_to_nanoerg(0.001),  # Minimum box value
                "tokens": [
                    {
                        "id": token_id,
                        "amount": recipient["amount"]
                    }
                ],
                "registers": {}
            }
            outputs.append(output)
        
        # Build transaction
        transaction = self.wallet_manager.create_transaction(
            outputs=outputs,
            fee_erg=fee_erg
        )
        
        # Sign and broadcast
        signed_tx = self.wallet_manager.sign_transaction(transaction)
        tx_id = self.network_manager.broadcast_transaction(signed_tx)
        
        return tx_id
    
    def _validate_distribution_config(self, config: Dict[str, Any]) -> None:
        """Validate token distribution configuration."""
        if "recipients" not in config:
            raise ValueError("Configuration must contain 'recipients' section")
        
        recipients = config["recipients"]
        if not isinstance(recipients, list) or len(recipients) == 0:
            raise ValueError("'recipients' must be a non-empty list")
        
        for i, recipient in enumerate(recipients):
            if not isinstance(recipient, dict):
                raise ValueError(f"Recipient {i+1} must be a dictionary")
            
            if "address" not in recipient:
                raise ValueError(f"Recipient {i+1} must have an 'address' field")
            
            if "amount" not in recipient:
                raise ValueError(f"Recipient {i+1} must have an 'amount' field")
            
            if not isinstance(recipient["amount"], (int, float)):
                raise ValueError(f"Recipient {i+1} amount must be a number")
    
    def get_token_balance(self, address: str, token_id: str) -> int:
        """
        Get token balance for an address.
        
        Args:
            address: Address to check
            token_id: Token ID to check
            
        Returns:
            Token balance
        """
        try:
            balance_info = self.network_manager.get_address_balance(address)
            tokens = balance_info.get("tokens", [])
            
            for token in tokens:
                if token.get("tokenId") == token_id:
                    return token.get("amount", 0)
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Failed to get token balance: {e}")
            return 0
    
    def get_token_info(self, token_id: str) -> Dict[str, Any]:
        """
        Get token information.
        
        Args:
            token_id: Token ID to lookup
            
        Returns:
            Dictionary containing token information
        """
        return self.network_manager.get_token_info(token_id)
    
    def estimate_distribution_cost(
        self,
        recipient_count: int,
        batch_size: int = 50,
        fee_per_tx: float = 0.001
    ) -> Dict[str, Any]:
        """
        Estimate cost for token distribution.
        
        Args:
            recipient_count: Number of recipients
            batch_size: Recipients per transaction
            fee_per_tx: Fee per transaction
            
        Returns:
            Dictionary containing cost estimates
        """
        num_transactions = math.ceil(recipient_count / batch_size)
        total_fee_erg = num_transactions * fee_per_tx
        min_box_value_erg = recipient_count * 0.001
        total_cost_erg = total_fee_erg + min_box_value_erg
        
        return {
            "recipients": recipient_count,
            "transactions": num_transactions,
            "fee_per_tx": fee_per_tx,
            "total_fees": total_fee_erg,
            "min_box_values": min_box_value_erg,
            "total_cost": total_cost_erg,
            "batch_size": batch_size
        }
    
    def __str__(self) -> str:
        """String representation of TokenManager."""
        return "TokenManager()"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"TokenManager(network={self.network_manager.network})"