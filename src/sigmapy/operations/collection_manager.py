"""
CollectionManager - EIP-24 compliant collection token operations

This class provides methods for:
- Creating collection tokens (fungible tokens that serve as collection IDs)
- Managing collection metadata and properties
- Handling collection-level royalty structures
- Supporting complex multi-recipient royalties

Based on EIP-24 Artwork Contract standard:
https://docs.ergoplatform.com/dev/tokens/standards/eip24/
"""

from typing import Dict, List, Optional, Any, Union
import logging
from pathlib import Path
import yaml

from ..utils import AmountUtils
from ..config import ConfigParser

try:
    import ergo_lib_python as ergo
    ERGO_LIB_AVAILABLE = True
except ImportError:
    ERGO_LIB_AVAILABLE = False
    ergo = None


class CollectionManager:
    """
    Collection management operations with EIP-24 compliance.
    
    This class provides methods for creating and managing collection tokens
    that serve as identifiers for NFT collections according to EIP-24 standard.
    """
    
    # Minimum ERG per output box (Ergo protocol requirement)
    MIN_BOX_VALUE_NANOERG = 1_000_000  # 0.001 ERG
    
    def __init__(self, wallet_manager, network_manager, dry_run: bool = False):
        """
        Initialize CollectionManager.
        
        Args:
            wallet_manager: WalletManager instance for signing
            network_manager: NetworkManager instance for broadcasting
            dry_run: If True, build transactions but don't broadcast
        """
        self.wallet_manager = wallet_manager
        self.network_manager = network_manager
        self.dry_run = dry_run
        self.logger = logging.getLogger(__name__)
    
    def create_collection_token(
        self, 
        name: str, 
        description: str, 
        supply: int,
        royalties: Optional[List[Dict[str, Any]]] = None,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a collection token according to EIP-24 standard.
        
        Args:
            name: Collection name
            description: Collection description
            supply: Total supply of collection tokens (should be > number of NFTs)
            royalties: List of royalty recipients with addresses and percentages
            additional_metadata: Additional collection-level metadata
            
        Returns:
            Transaction ID (or demo ID in dry-run mode)
            
        Example:
            >>> collection_id = manager.create_collection_token(
            ...     name="My Art Collection",
            ...     description="Digital artwork series",
            ...     supply=10000,
            ...     royalties=[{"address": "9f...", "percentage": 5}]
            ... )
        """
        self.logger.info(f"Creating collection token: {name}")
        self.logger.info(f"Supply: {supply}, Royalties: {len(royalties or [])}")
        
        # Validate royalties
        if royalties:
            total_percentage = sum(r.get('percentage', 0) for r in royalties)
            if total_percentage > 100:
                raise ValueError(f"Total royalty percentage ({total_percentage}%) exceeds 100%")
            
            for i, royalty in enumerate(royalties):
                if 'address' not in royalty or 'percentage' not in royalty:
                    raise ValueError(f"Royalty {i+1} missing required 'address' or 'percentage'")
                if not self.wallet_manager.validate_address(royalty['address']):
                    raise ValueError(f"Invalid royalty address: {royalty['address']}")
                if not 0 <= royalty['percentage'] <= 100:
                    raise ValueError(f"Invalid royalty percentage: {royalty['percentage']}%")
        
        # Build collection token metadata
        token_metadata = self._build_collection_metadata(
            name, description, supply, royalties, additional_metadata
        )
        
        if self.dry_run:
            # Dry run mode
            tx_data = self._build_collection_creation_transaction(token_metadata)
            self._log_dry_run_collection_creation(tx_data, name, supply, royalties)
            return "dry_run_collection_creation"
        else:
            # Real transaction
            return self._execute_collection_creation(token_metadata)
    
    def create_collection_from_config(self, config_file: Union[str, Path]) -> str:
        """
        Create a collection token from a YAML configuration file.
        
        Args:
            config_file: Path to YAML configuration file
            
        Returns:
            Transaction ID
            
        Example config:
            collection:
              name: "My Art Collection"
              description: "Digital artwork series"
              supply: 10000
              royalties:
                - address: "9fArtist..."
                  percentage: 85
                - address: "9fCharity..."
                  percentage: 15
        """
        self.logger.info(f"Loading collection config from {config_file}")
        
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        collection = config.get('collection', {})
        
        if not collection.get('name'):
            raise ValueError("Collection name is required")
        if not collection.get('description'):
            raise ValueError("Collection description is required")
        if not collection.get('supply'):
            raise ValueError("Collection supply is required")
        
        return self.create_collection_token(
            name=collection['name'],
            description=collection['description'],
            supply=collection['supply'],
            royalties=collection.get('royalties', []),
            additional_metadata=collection.get('additional_metadata', {})
        )
    
    def _build_collection_metadata(
        self, 
        name: str, 
        description: str, 
        supply: int,
        royalties: Optional[List[Dict[str, Any]]] = None,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Build EIP-24 compliant collection token metadata."""
        metadata = {
            'name': name,
            'description': description,
            'supply': supply,
            'decimals': 0,  # Collection tokens are typically non-divisible
            'type': 'Collection Token',
            'standard': 'EIP-24'
        }
        
        # Add royalties if specified
        if royalties:
            metadata['royalties'] = royalties
        
        # Add additional metadata
        if additional_metadata:
            metadata.update(additional_metadata)
        
        return metadata
    
    def _build_collection_creation_transaction(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Build a collection token creation transaction."""
        if not ERGO_LIB_AVAILABLE:
            # Demo mode transaction
            return {
                "type": "collection_creation",
                "metadata": metadata,
                "fee_nanoerg": AmountUtils.erg_to_nanoerg(0.001),
                "demo_mode": True
            }
        
        try:
            # Get sender address and UTXOs
            sender_address = self.wallet_manager.get_primary_address()
            sender_utxos = self.network_manager.get_address_utxos(sender_address)
            
            # Create transaction builder
            tx_builder = ergo.TxBuilder()
            fee_nanoerg = AmountUtils.erg_to_nanoerg(0.001)
            
            # Calculate ERG needed (minimum box value + fee)
            total_erg_needed = self.MIN_BOX_VALUE_NANOERG + fee_nanoerg
            selected_utxos, available_erg = self._select_erg_utxos(sender_utxos, total_erg_needed)
            
            if available_erg < total_erg_needed:
                raise ValueError(
                    f"Insufficient ERG: need {AmountUtils.nanoerg_to_erg(total_erg_needed)}, "
                    f"have {AmountUtils.nanoerg_to_erg(available_erg)}"
                )
            
            # Add inputs
            for utxo in selected_utxos:
                tx_builder.add_input(self._utxo_to_input(utxo))
            
            # Add collection token creation output
            collection_output = self._create_collection_token_output(
                sender_address, metadata, self.MIN_BOX_VALUE_NANOERG
            )
            tx_builder.add_output(collection_output)
            
            # Add change output if needed
            change_erg = available_erg - total_erg_needed
            if change_erg > self.MIN_BOX_VALUE_NANOERG:
                change_output = self._create_change_output(sender_address, change_erg)
                tx_builder.add_output(change_output)
            
            # Build unsigned transaction
            unsigned_tx = tx_builder.build()
            
            return {
                "unsigned_tx": unsigned_tx,
                "metadata": metadata,
                "fee_nanoerg": fee_nanoerg,
                "total_erg": total_erg_needed,
                "demo_mode": False
            }
            
        except Exception as e:
            self.logger.error(f"Failed to build collection creation transaction: {e}")
            raise
    
    def _execute_collection_creation(self, metadata: Dict[str, Any]) -> str:
        """Execute collection token creation."""
        try:
            # Build transaction
            tx_data = self._build_collection_creation_transaction(metadata)
            
            # Sign transaction
            if not tx_data.get("demo_mode", False):
                signed_tx = self.wallet_manager.sign_transaction(tx_data["unsigned_tx"])
            else:
                signed_tx = tx_data
            
            # Broadcast transaction
            tx_id = self.network_manager.broadcast_transaction(signed_tx)
            
            self.logger.info(f"Collection token created. Transaction ID: {tx_id}")
            return tx_id
            
        except Exception as e:
            self.logger.error(f"Failed to execute collection creation: {e}")
            raise
    
    def _create_collection_token_output(
        self, 
        address: str, 
        metadata: Dict[str, Any], 
        erg_value: int
    ):
        """Create an output containing the collection token."""
        if not ERGO_LIB_AVAILABLE:
            return {
                "address": address,
                "value": erg_value,
                "registers": self._encode_collection_registers(metadata)
            }
        
        # Create actual ergo-lib output
        addr = ergo.Address.from_base58(address)
        value = ergo.BoxValue.from_i64(erg_value)
        
        # Create output builder
        output_builder = ergo.ErgoBoxCandidateBuilder(value, addr)
        
        # Add registers with collection metadata
        registers = self._encode_collection_registers(metadata)
        for reg_id, reg_value in registers.items():
            output_builder.add_register(reg_id, reg_value)
        
        return output_builder.build()
    
    def _encode_collection_registers(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Encode collection metadata into EIP-24 compliant registers."""
        registers = {}
        
        # R4: Collection name
        if 'name' in metadata:
            registers['R4'] = metadata['name']
        
        # R5: Royalty information
        if 'royalties' in metadata:
            registers['R5'] = self._encode_royalties(metadata['royalties'])
        
        # R6: Collection properties/traits
        collection_traits = {
            'type': 'collection',
            'supply': metadata.get('supply', 0),
            'standard': metadata.get('standard', 'EIP-24')
        }
        registers['R6'] = collection_traits
        
        # R7: Not used for collection tokens (used by NFTs to reference collection)
        
        # R8: Additional metadata
        if 'additional_metadata' in metadata and metadata['additional_metadata']:
            registers['R8'] = metadata['additional_metadata']
        
        return registers
    
    def _encode_royalties(self, royalties: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Encode royalty information for EIP-24 compliance."""
        return {
            'recipients': [
                {
                    'address': r['address'],
                    'percentage': r['percentage']
                }
                for r in royalties
            ],
            'total_percentage': sum(r['percentage'] for r in royalties)
        }
    
    def _select_erg_utxos(self, utxos: List[Dict], erg_needed: int) -> tuple[List[Dict], int]:
        """Select UTXOs containing sufficient ERG."""
        selected = []
        total_erg = 0
        
        for utxo in utxos:
            selected.append(utxo)
            total_erg += utxo['value']
            if total_erg >= erg_needed:
                break
        
        return selected, total_erg
    
    def _create_change_output(self, address: str, erg_value: int):
        """Create a change output."""
        if not ERGO_LIB_AVAILABLE:
            return {
                "address": address,
                "value": erg_value
            }
        
        addr = ergo.Address.from_base58(address)
        value = ergo.BoxValue.from_i64(erg_value)
        
        output_builder = ergo.ErgoBoxCandidateBuilder(value, addr)
        return output_builder.build()
    
    def _utxo_to_input(self, utxo: Dict):
        """Convert UTXO dict to ergo-lib input."""
        if not ERGO_LIB_AVAILABLE:
            return utxo
        
        box_id = ergo.BoxId.from_str(utxo['box_id'])
        return ergo.UnsignedInput(box_id)
    
    def _log_dry_run_collection_creation(
        self, 
        tx_data: Dict, 
        name: str, 
        supply: int, 
        royalties: Optional[List[Dict[str, Any]]]
    ):
        """Log details of a dry-run collection creation."""
        self.logger.info("=== DRY RUN COLLECTION CREATION ===")
        self.logger.info(f"Collection Name: {name}")
        self.logger.info(f"Supply: {supply}")
        
        if royalties:
            self.logger.info(f"Royalties ({len(royalties)} recipients):")
            for i, royalty in enumerate(royalties):
                self.logger.info(f"  {i+1}. {royalty['address'][:10]}... {royalty['percentage']}%")
            total_royalty = sum(r['percentage'] for r in royalties)
            self.logger.info(f"Total royalty percentage: {total_royalty}%")
        else:
            self.logger.info("No royalties specified")
        
        self.logger.info(f"Transaction fee: {AmountUtils.nanoerg_to_erg(tx_data['fee_nanoerg'])} ERG")
        self.logger.info(f"Minimum box value: {AmountUtils.nanoerg_to_erg(self.MIN_BOX_VALUE_NANOERG)} ERG")
        
        if not tx_data.get('demo_mode', True):
            self.logger.info(f"Total ERG required: {AmountUtils.nanoerg_to_erg(tx_data['total_erg'])} ERG")
        
        self.logger.info("=== END DRY RUN ===")
    
    def validate_collection_config(self, config_file: Union[str, Path]) -> Dict[str, Any]:
        """
        Validate a collection configuration file.
        
        Args:
            config_file: Path to YAML configuration file
            
        Returns:
            Validation result with summary
        """
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            collection = config.get('collection', {})
            
            # Validate required fields
            errors = []
            warnings = []
            
            if not collection.get('name'):
                errors.append("Missing required field: collection.name")
            
            if not collection.get('description'):
                errors.append("Missing required field: collection.description")
            
            if not collection.get('supply'):
                errors.append("Missing required field: collection.supply")
            elif not isinstance(collection['supply'], int) or collection['supply'] <= 0:
                errors.append("Collection supply must be a positive integer")
            
            # Validate royalties
            royalties = collection.get('royalties', [])
            if royalties:
                total_percentage = 0
                for i, royalty in enumerate(royalties):
                    if 'address' not in royalty:
                        errors.append(f"Royalty {i+1} missing address")
                    elif not self.wallet_manager.validate_address(royalty['address']):
                        errors.append(f"Invalid address in royalty {i+1}: {royalty['address']}")
                    
                    if 'percentage' not in royalty:
                        errors.append(f"Royalty {i+1} missing percentage")
                    elif not isinstance(royalty['percentage'], (int, float)) or not 0 <= royalty['percentage'] <= 100:
                        errors.append(f"Invalid percentage in royalty {i+1}: {royalty['percentage']}")
                    else:
                        total_percentage += royalty['percentage']
                
                if total_percentage > 100:
                    errors.append(f"Total royalty percentage ({total_percentage}%) exceeds 100%")
                elif total_percentage > 50:
                    warnings.append(f"High total royalty percentage: {total_percentage}%")
            
            # Calculate costs
            fee_erg = 0.001
            min_erg_needed = float(AmountUtils.nanoerg_to_erg(self.MIN_BOX_VALUE_NANOERG))
            total_cost = fee_erg + min_erg_needed
            
            summary = {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "collection_name": collection.get('name', 'Unknown'),
                "supply": collection.get('supply', 0),
                "royalty_count": len(royalties),
                "total_royalty_percentage": sum(r.get('percentage', 0) for r in royalties),
                "transaction_fee": fee_erg,
                "min_erg_needed": min_erg_needed,
                "total_cost": total_cost
            }
            
            return summary
            
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Failed to parse config file: {e}"],
                "warnings": []
            }
    
    def create_collection_template(self, output_file: Union[str, Path]):
        """Create a template collection configuration YAML file."""
        template = {
            "collection": {
                "name": "My Art Collection",
                "description": "A unique digital art collection",
                "supply": 10000,
                "royalties": [
                    {
                        "address": "9fArtistAddressHere...",
                        "percentage": 85
                    },
                    {
                        "address": "9fCharityAddressHere...",
                        "percentage": 15
                    }
                ],
                "additional_metadata": {
                    "website": "https://example.com",
                    "twitter": "@artcollection"
                }
            }
        }
        
        with open(output_file, 'w') as f:
            yaml.dump(template, f, default_flow_style=False, indent=2)
        
        self.logger.info(f"Collection configuration template created: {output_file}")
    
    def get_dry_run_mode(self) -> bool:
        """Check if in dry-run mode."""
        return self.dry_run
    
    def set_dry_run_mode(self, dry_run: bool):
        """Set dry-run mode."""
        self.dry_run = dry_run
        self.logger.info(f"Dry-run mode {'enabled' if dry_run else 'disabled'}")