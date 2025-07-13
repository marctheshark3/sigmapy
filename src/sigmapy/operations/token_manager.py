"""
TokenManager - Token operations with real blockchain integration

This class provides methods for:
- Token creation and minting
- Token distribution and transfers
- Batch token operations
- Airdrop functionality with YAML config support
"""

from typing import Dict, List, Optional, Any, Union
import logging
from pathlib import Path
import math
import yaml

from ..utils import AmountUtils
from ..config import ConfigParser

try:
    import ergo_lib_python as ergo
    ERGO_LIB_AVAILABLE = True
except ImportError:
    ERGO_LIB_AVAILABLE = False
    ergo = None


class TokenManager:
    """
    Token management operations with real blockchain integration.
    
    This class provides methods for creating and managing tokens
    with automatic batch processing and proper transaction building.
    """
    
    # Minimum ERG per output box (Ergo protocol requirement)
    MIN_BOX_VALUE_NANOERG = 1_000_000  # 0.001 ERG
    
    def __init__(self, wallet_manager, network_manager, dry_run: bool = False):
        """
        Initialize TokenManager.
        
        Args:
            wallet_manager: WalletManager instance for signing
            network_manager: NetworkManager instance for broadcasting
            dry_run: If True, build transactions but don't broadcast
        """
        self.wallet_manager = wallet_manager
        self.network_manager = network_manager
        self.dry_run = dry_run
        self.logger = logging.getLogger(__name__)
    
    def distribute_tokens_from_config(self, config_file: Union[str, Path]) -> str:
        """
        Distribute tokens according to a YAML configuration file.
        
        Args:
            config_file: Path to YAML configuration file
            
        Returns:
            Transaction ID (single transaction for all recipients)
            
        Example config:
            distribution:
              token_id: "abc123..."
              fee_per_tx: 0.001
            recipients:
              - address: "9f..."
                amount: 100
                note: "Community member"
        """
        self.logger.info(f"Loading token distribution config from {config_file}")
        
        # Load configuration
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        distribution = config.get('distribution', {})
        recipients = config.get('recipients', [])
        
        token_id = distribution.get('token_id')
        if not token_id:
            raise ValueError("token_id is required in distribution config")
        
        fee_per_tx = distribution.get('fee_per_tx', 0.001)
        
        # Fetch token information from the node - always agnostic, use node data
        token_info = self._get_token_info(token_id)
        decimals = token_info.get('decimals', 0)
        token_name = token_info.get('name', 'Unknown Token')
        
        self.logger.info(f"Distributing token {token_name} ({token_id}) to {len(recipients)} recipients in single transaction")
        self.logger.info(f"Token decimals from node: {decimals}")
        self.logger.info(f"Transaction fee: {fee_per_tx} ERG")
        
        # Validate all addresses
        for recipient in recipients:
            address = recipient['address']
            if not self.wallet_manager.validate_address(address):
                raise ValueError(f"Invalid address: {address}")
        
        # Validate token amounts considering decimals
        for i, recipient in enumerate(recipients):
            amount = recipient.get('amount', 0)
            if decimals > 0:
                # Check if amount is properly formatted for token decimals
                max_amount = 10 ** decimals
                if amount <= 0:
                    raise ValueError(f"Recipient {i+1}: amount must be positive")
                if amount != int(amount):
                    # Allow fractional amounts only if they respect decimal places from node
                    scaled_amount = amount * (10 ** decimals)
                    if scaled_amount != int(scaled_amount):
                        raise ValueError(f"Recipient {i+1}: amount {amount} has too many decimal places for token with {decimals} decimals (from node data)")
        
        # Process all recipients in single transaction
        self.logger.info(f"Processing all {len(recipients)} recipients in single transaction")
        
        if self.dry_run:
            # Dry run mode - build transaction but don't broadcast
            tx_data = self._build_token_distribution_transaction(
                token_id, recipients, fee_per_tx, token_info
            )
            self._log_dry_run_transaction(tx_data, recipients, token_info)
            tx_id = "dry_run_single_transaction"
        else:
            # Real transaction
            tx_id = self._execute_token_distribution_batch(
                token_id, recipients, fee_per_tx, token_info
            )
        
        self.logger.info(f"Token distribution completed. Transaction created: {tx_id}")
        return tx_id
    
    def _get_token_info(self, token_id: str) -> Dict[str, Any]:
        """
        Get token information from the Ergo node.
        Always agnostic - relies completely on node-supplied data.
        
        Args:
            token_id: Token ID to lookup
            
        Returns:
            Dictionary containing token information including decimals from node
        """
        try:
            # Use NetworkManager to get token info from node
            self.logger.debug(f"Fetching token info from node for: {token_id}")
            token_info = self.network_manager.get_token_info(token_id)
            
            # Parse decimals agnostically from whatever the node provides
            decimals = 0
            name = 'Unknown Token'
            description = ''
            token_type = 'Token'
            
            # Extract all possible decimal field locations from node response
            if 'decimals' in token_info:
                decimals = int(token_info['decimals'])
                self.logger.debug(f"Found decimals in root: {decimals}")
            elif 'additionalInfo' in token_info:
                additional_info = token_info['additionalInfo']
                if 'decimals' in additional_info:
                    decimals = int(additional_info['decimals'])
                    self.logger.debug(f"Found decimals in additionalInfo: {decimals}")
            elif 'registers' in token_info:
                # Some tokens store decimals in registers
                registers = token_info['registers']
                for reg_key, reg_value in registers.items():
                    if 'decimals' in str(reg_value).lower():
                        try:
                            decimals = int(reg_value)
                            self.logger.debug(f"Found decimals in register {reg_key}: {decimals}")
                            break
                        except (ValueError, TypeError):
                            continue
            
            # Extract other fields from node data
            if 'name' in token_info:
                name = token_info['name']
            if 'description' in token_info:
                description = token_info['description']
            if 'type' in token_info:
                token_type = token_info['type']
            
            result = {
                'id': token_id,
                'name': name,
                'description': description,
                'decimals': decimals,
                'type': token_type,
                'raw_info': token_info,
                'node_supplied': True
            }
            
            self.logger.info(f"Token info from node: {name} (decimals: {decimals})")
            return result
            
        except Exception as e:
            self.logger.warning(f"Could not fetch token info from node for {token_id}: {e}")
            self.logger.warning("Using fallback defaults - decimals will be 0")
            # Return minimal fallback - only when node is completely unavailable
            return {
                'id': token_id,
                'name': 'Unknown Token',
                'description': '',
                'decimals': 0,
                'type': 'Token',
                'raw_info': {},
                'node_supplied': False
            }
    
    def _convert_token_amount_to_smallest_unit(self, amount: Union[int, float], decimals: int) -> int:
        """
        Convert token amount to smallest unit based on decimals.
        
        Args:
            amount: Token amount (can be fractional)
            decimals: Number of decimal places
            
        Returns:
            Amount in smallest unit (integer)
        """
        if decimals == 0:
            return int(amount)
        
        smallest_unit_amount = amount * (10 ** decimals)
        return int(smallest_unit_amount)
    
    def _format_token_amount_for_display(self, amount: int, decimals: int) -> str:
        """
        Format token amount for display considering decimals.
        
        Args:
            amount: Amount in smallest unit
            decimals: Number of decimal places
            
        Returns:
            Formatted amount string
        """
        if decimals == 0:
            return str(amount)
        
        divisor = 10 ** decimals
        display_amount = amount / divisor
        
        # Format to remove unnecessary trailing zeros
        if display_amount == int(display_amount):
            return str(int(display_amount))
        else:
            return f"{display_amount:.{decimals}f}".rstrip('0').rstrip('.')
    
    def _build_token_distribution_transaction(
        self, 
        token_id: str, 
        recipients: List[Dict], 
        fee_erg: float,
        token_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Build a token distribution transaction."""
        if token_info is None:
            token_info = self._get_token_info(token_id)
        
        decimals = token_info.get('decimals', 0)
        
        # Convert amounts to smallest units for transaction
        converted_recipients = []
        total_tokens_smallest_unit = 0
        
        for recipient in recipients:
            amount = recipient['amount']
            amount_smallest_unit = self._convert_token_amount_to_smallest_unit(amount, decimals)
            converted_recipients.append({
                **recipient,
                'amount_smallest_unit': amount_smallest_unit
            })
            total_tokens_smallest_unit += amount_smallest_unit
        
        if not ERGO_LIB_AVAILABLE:
            # Demo mode transaction
            return {
                "type": "token_distribution",
                "token_id": token_id,
                "recipients": converted_recipients,
                "fee_nanoerg": AmountUtils.erg_to_nanoerg(fee_erg),
                "total_tokens": total_tokens_smallest_unit,
                "total_tokens_display": sum(r['amount'] for r in recipients),
                "outputs": len(recipients),
                "demo_mode": True,
                "token_info": token_info
            }
        
        try:
            # Get sender address and UTXOs
            sender_address = self.wallet_manager.get_primary_address()
            sender_utxos = self.network_manager.get_address_utxos(sender_address)
            
            # Create transaction builder
            tx_builder = ergo.TxBuilder()
            fee_nanoerg = AmountUtils.erg_to_nanoerg(fee_erg)
            
            # Find UTXOs with the required tokens (in smallest units)
            selected_utxos, available_tokens = self._select_token_utxos(
                sender_utxos, token_id, total_tokens_smallest_unit
            )
            
            if available_tokens < total_tokens_smallest_unit:
                display_needed = self._format_token_amount_for_display(total_tokens_smallest_unit, decimals)
                display_available = self._format_token_amount_for_display(available_tokens, decimals)
                raise ValueError(
                    f"Insufficient tokens: need {display_needed}, have {display_available}"
                )
            
            # Calculate total ERG needed (minimum box values + fee)
            total_erg_needed = len(recipients) * self.MIN_BOX_VALUE_NANOERG + fee_nanoerg
            selected_utxos, available_erg = self._select_erg_utxos(
                sender_utxos, total_erg_needed, selected_utxos
            )
            
            if available_erg < total_erg_needed:
                raise ValueError(
                    f"Insufficient ERG: need {AmountUtils.nanoerg_to_erg(total_erg_needed)}, "
                    f"have {AmountUtils.nanoerg_to_erg(available_erg)}"
                )
            
            # Add inputs
            for utxo in selected_utxos:
                tx_builder.add_input(self._utxo_to_input(utxo))
            
            # Add outputs for recipients (using smallest units)
            for recipient in converted_recipients:
                output = self._create_token_output(
                    recipient['address'], 
                    token_id, 
                    recipient['amount_smallest_unit'],
                    self.MIN_BOX_VALUE_NANOERG
                )
                tx_builder.add_output(output)
            
            # Add change output if needed
            change_erg = available_erg - (len(recipients) * self.MIN_BOX_VALUE_NANOERG + fee_nanoerg)
            change_tokens = available_tokens - total_tokens_smallest_unit
            
            if change_erg > self.MIN_BOX_VALUE_NANOERG or change_tokens > 0:
                change_output = self._create_change_output(
                    sender_address, change_erg, token_id, change_tokens
                )
                tx_builder.add_output(change_output)
            
            # Build unsigned transaction
            unsigned_tx = tx_builder.build()
            
            return {
                "unsigned_tx": unsigned_tx,
                "token_id": token_id,
                "recipients": converted_recipients,
                "fee_nanoerg": fee_nanoerg,
                "total_tokens": total_tokens_smallest_unit,
                "total_tokens_display": sum(r['amount'] for r in recipients),
                "total_erg": total_erg_needed,
                "demo_mode": False,
                "token_info": token_info
            }
            
        except Exception as e:
            self.logger.error(f"Failed to build token distribution transaction: {e}")
            raise
    
    def _execute_token_distribution_batch(
        self, 
        token_id: str, 
        recipients: List[Dict], 
        fee_erg: float,
        token_info: Optional[Dict[str, Any]] = None
    ) -> str:
        """Execute a batch of token distribution."""
        try:
            # Build transaction
            tx_data = self._build_token_distribution_transaction(token_id, recipients, fee_erg, token_info)
            
            # Sign transaction
            if not tx_data.get("demo_mode", False):
                signed_tx = self.wallet_manager.sign_transaction(tx_data["unsigned_tx"])
            else:
                signed_tx = tx_data
            
            # Broadcast transaction
            tx_id = self.network_manager.broadcast_transaction(signed_tx)
            
            self.logger.info(f"Token distribution batch completed. Transaction ID: {tx_id}")
            return tx_id
            
        except Exception as e:
            self.logger.error(f"Failed to execute token distribution batch: {e}")
            raise
    
    def _select_token_utxos(
        self, 
        utxos: List[Dict], 
        token_id: str, 
        amount_needed: int
    ) -> tuple[List[Dict], int]:
        """Select UTXOs containing the required tokens."""
        selected = []
        total_tokens = 0
        
        for utxo in utxos:
            for token in utxo.get('tokens', []):
                if token.get('tokenId') == token_id or token.get('id') == token_id:
                    selected.append(utxo)
                    total_tokens += token.get('amount', 0)
                    if total_tokens >= amount_needed:
                        return selected, total_tokens
        
        return selected, total_tokens
    
    def _select_erg_utxos(
        self, 
        utxos: List[Dict], 
        erg_needed: int, 
        exclude_utxos: List[Dict] = None
    ) -> tuple[List[Dict], int]:
        """Select UTXOs containing sufficient ERG."""
        if exclude_utxos is None:
            exclude_utxos = []
        
        exclude_ids = {utxo['box_id'] for utxo in exclude_utxos}
        selected = list(exclude_utxos)  # Start with already selected UTXOs
        total_erg = sum(utxo['value'] for utxo in exclude_utxos)
        
        for utxo in utxos:
            if utxo['box_id'] not in exclude_ids and total_erg < erg_needed:
                selected.append(utxo)
                total_erg += utxo['value']
        
        return selected, total_erg
    
    def _create_token_output(self, address: str, token_id: str, token_amount: int, erg_value: int):
        """Create an output containing tokens."""
        if not ERGO_LIB_AVAILABLE:
            return {
                "address": address,
                "value": erg_value,
                "tokens": [{"id": token_id, "amount": token_amount}]
            }
        
        # Create actual ergo-lib output
        addr = ergo.Address.from_base58(address)
        value = ergo.BoxValue.from_i64(erg_value)
        
        # Create token
        token = ergo.Token(ergo.TokenId.from_str(token_id), ergo.TokenAmount.from_i64(token_amount))
        tokens = ergo.Tokens([token])
        
        # Create output
        output_builder = ergo.ErgoBoxCandidateBuilder(value, addr)
        output_builder.set_tokens(tokens)
        
        return output_builder.build()
    
    def _create_change_output(self, address: str, erg_value: int, token_id: str, token_amount: int):
        """Create a change output."""
        if not ERGO_LIB_AVAILABLE:
            return {
                "address": address,
                "value": erg_value,
                "tokens": [{"id": token_id, "amount": token_amount}] if token_amount > 0 else []
            }
        
        addr = ergo.Address.from_base58(address)
        value = ergo.BoxValue.from_i64(erg_value)
        
        output_builder = ergo.ErgoBoxCandidateBuilder(value, addr)
        
        if token_amount > 0:
            token = ergo.Token(ergo.TokenId.from_str(token_id), ergo.TokenAmount.from_i64(token_amount))
            tokens = ergo.Tokens([token])
            output_builder.set_tokens(tokens)
        
        return output_builder.build()
    
    def _utxo_to_input(self, utxo: Dict):
        """Convert UTXO dict to ergo-lib input."""
        if not ERGO_LIB_AVAILABLE:
            return utxo
        
        box_id = ergo.BoxId.from_str(utxo['box_id'])
        return ergo.UnsignedInput(box_id)
    
    def _log_dry_run_transaction(self, tx_data: Dict, recipients: List[Dict], token_info: Optional[Dict[str, Any]] = None):
        """Log details of a dry-run transaction."""
        if token_info is None:
            token_info = tx_data.get('token_info', {})
        
        decimals = token_info.get('decimals', 0)
        token_name = token_info.get('name', 'Unknown Token')
        
        self.logger.info("=== DRY RUN TRANSACTION ===")
        self.logger.info(f"Token: {token_name} ({tx_data['token_id']})")
        self.logger.info(f"Token decimals: {decimals}")
        self.logger.info(f"Total recipients: {len(recipients)}")
        
        # Show both display and smallest unit amounts
        display_total = tx_data.get('total_tokens_display', sum(r['amount'] for r in recipients))
        smallest_unit_total = tx_data.get('total_tokens', 0)
        
        if decimals > 0:
            self.logger.info(f"Total tokens to distribute: {display_total} ({smallest_unit_total} smallest units)")
        else:
            self.logger.info(f"Total tokens to distribute: {display_total}")
        
        self.logger.info(f"Transaction fee: {AmountUtils.nanoerg_to_erg(tx_data['fee_nanoerg'])} ERG")
        self.logger.info(f"Minimum box values: {len(recipients) * AmountUtils.nanoerg_to_erg(self.MIN_BOX_VALUE_NANOERG)} ERG")
        
        self.logger.info("Recipients:")
        for i, recipient in enumerate(recipients):
            note = recipient.get('note', '')
            amount = recipient['amount']
            amount_display = f"{amount}"
            
            # Show smallest unit amount if it's different
            if 'amount_smallest_unit' in recipient and decimals > 0:
                smallest_unit = recipient['amount_smallest_unit']
                if smallest_unit != amount:
                    amount_display = f"{amount} ({smallest_unit} units)"
            
            self.logger.info(f"  {i+1}. {recipient['address'][:10]}... {amount_display} tokens {note}")
        
        if not tx_data.get('demo_mode', True):
            self.logger.info(f"Total ERG required: {AmountUtils.nanoerg_to_erg(tx_data['total_erg'])} ERG")
        
        self.logger.info("=== END DRY RUN ===")
    
    def validate_distribution_config(self, config_file: Union[str, Path]) -> Dict[str, Any]:
        """
        Validate a token distribution configuration file.
        
        Args:
            config_file: Path to YAML configuration file
            
        Returns:
            Validation result with summary
        """
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            distribution = config.get('distribution', {})
            recipients = config.get('recipients', [])
            
            # Validate required fields
            errors = []
            warnings = []
            
            if not distribution.get('token_id'):
                errors.append("Missing required field: distribution.token_id")
            
            if not recipients:
                errors.append("No recipients specified")
            
            # Validate addresses
            invalid_addresses = []
            for i, recipient in enumerate(recipients):
                if 'address' not in recipient:
                    errors.append(f"Missing address for recipient {i+1}")
                    continue
                
                if not self.wallet_manager.validate_address(recipient['address']):
                    invalid_addresses.append(f"Recipient {i+1}: {recipient['address']}")
                
                if 'amount' not in recipient or recipient['amount'] <= 0:
                    errors.append(f"Invalid amount for recipient {i+1}")
            
            if invalid_addresses:
                errors.extend([f"Invalid address: {addr}" for addr in invalid_addresses])
            
            # Calculate totals for single transaction
            total_recipients = len(recipients)
            total_tokens = sum(r.get('amount', 0) for r in recipients)
            fee_per_tx = distribution.get('fee_per_tx', 0.001)
            
            # Calculate costs for single transaction (no batching)
            min_erg_needed = float(total_recipients * AmountUtils.nanoerg_to_erg(self.MIN_BOX_VALUE_NANOERG))
            total_fees = float(fee_per_tx)  # Single transaction fee
            total_erg_needed = min_erg_needed + total_fees
            
            # Add warning for large recipient counts
            if total_recipients > 100:
                warnings.append(f"Large recipient count ({total_recipients}). Consider testing with smaller amounts first.")
            
            summary = {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "total_recipients": total_recipients,
                "total_tokens": total_tokens,
                "single_transaction": True,
                "min_erg_needed": min_erg_needed,
                "total_fees": total_fees,
                "total_erg_needed": total_erg_needed,
                "fee_per_tx": fee_per_tx
            }
            
            return summary
            
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Failed to parse config file: {e}"],
                "warnings": []
            }
    
    def create_distribution_template(self, output_file: Union[str, Path]):
        """Create a template token distribution YAML file."""
        template = {
            "distribution": {
                "token_id": "your_token_id_here",
                "fee_per_tx": 0.001,
            },
            "recipients": [
                {
                    "address": "9fRusAarL1KkrWQVsxSRVYnvWzD4dWoLLxbYk3eWBV3jD3qvr3W",
                    "amount": 100,
                    "note": "Community member"
                },
                {
                    "address": "9gQqZyxyjAptMbfW1Gydm3qaap11zd6X9DrABTbMBRJLjZhQRCA",
                    "amount": 150,
                    "note": "Developer contributor"
                }
            ]
        }
        
        with open(output_file, 'w') as f:
            yaml.dump(template, f, default_flow_style=False, indent=2)
        
        self.logger.info(f"Token distribution template created: {output_file}")
    
    def get_dry_run_mode(self) -> bool:
        """Check if in dry-run mode."""
        return self.dry_run
    
    def set_dry_run_mode(self, dry_run: bool):
        """Set dry-run mode."""
        self.dry_run = dry_run
        self.logger.info(f"Dry-run mode {'enabled' if dry_run else 'disabled'}")
    
    # TODO: Implement these methods
    def create_token(self, name: str, description: str, supply: int, decimals: int = 0, recipient: Optional[str] = None) -> str:
        """Create a new token - placeholder implementation."""
        self.logger.warning("create_token not yet implemented")
        return "demo_token_creation"
    
    def send_tokens(self, token_id: str, recipient: str, amount: int, fee_erg: float = 0.001) -> str:
        """Send tokens - placeholder implementation."""
        self.logger.warning("send_tokens not yet implemented")
        return "demo_token_send"
    
    def airdrop_tokens(self, token_id: str, addresses: List[str], amounts: List[int]) -> List[str]:
        """Airdrop tokens - placeholder implementation."""
        self.logger.warning("airdrop_tokens not yet implemented")
        return ["demo_airdrop_tx"]