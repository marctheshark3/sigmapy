"""
NFTMinter - EIP-24 compliant NFT minting operations

This class provides methods for:
- Single NFT minting with full EIP-24 register support (R4-R8)
- Sequential collection minting (N transactions for N NFTs)
- Artist identity verification through P2PK input chain
- Complex trait and metadata handling

Based on EIP-24 Artwork Contract standard:
https://docs.ergoplatform.com/dev/tokens/standards/eip24/
"""

from typing import Dict, List, Optional, Any, Union
import logging
from pathlib import Path
import yaml
import time

from ..utils import AmountUtils
from ..config import ConfigParser

try:
    import ergo_lib_python as ergo
    ERGO_LIB_AVAILABLE = True
except ImportError:
    ERGO_LIB_AVAILABLE = False
    ergo = None


class NFTMinter:
    """
    NFT minting operations with full EIP-24 compliance.
    
    This class provides methods for creating NFTs with proper register
    encoding according to EIP-24 standard, including support for collections,
    royalties, traits, and additional metadata.
    """
    
    # Minimum ERG per output box (Ergo protocol requirement)
    MIN_BOX_VALUE_NANOERG = 1_000_000  # 0.001 ERG
    
    def __init__(self, wallet_manager, network_manager, dry_run: bool = False):
        """
        Initialize NFTMinter.
        
        Args:
            wallet_manager: WalletManager instance for signing
            network_manager: NetworkManager instance for broadcasting
            dry_run: If True, build transactions but don't broadcast
        """
        self.wallet_manager = wallet_manager
        self.network_manager = network_manager
        self.dry_run = dry_run
        self.logger = logging.getLogger(__name__)
    
    def mint_nft(
        self,
        name: str,
        description: str,
        image_url: Optional[str] = None,
        collection_token_id: Optional[str] = None,
        royalties: Optional[List[Dict[str, Any]]] = None,
        traits: Optional[Dict[str, Any]] = None,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Mint a single NFT with EIP-24 compliance.
        
        Args:
            name: NFT name (stored in R4)
            description: NFT description
            image_url: URL to NFT image/content
            collection_token_id: Collection token ID for R7 (links to collection)
            royalties: List of royalty recipients for R5
            traits: NFT traits for R6 (properties, levels, stats)
            additional_metadata: Additional metadata for R8
            
        Returns:
            Transaction ID (or demo ID in dry-run mode)
            
        Example:
            >>> nft_id = minter.mint_nft(
            ...     name="Art #1",
            ...     description="First artwork in collection",
            ...     image_url="https://example.com/art1.png",
            ...     collection_token_id="abc123...",
            ...     royalties=[{"address": "9f...", "percentage": 5}],
            ...     traits={
            ...         "properties": {"background": "blue", "style": "abstract"},
            ...         "levels": {"rarity": {"value": 85, "max": 100}},
            ...         "stats": {"creation_year": 2024}
            ...     }
            ... )
        """
        self.logger.info(f"Minting NFT: {name}")
        if collection_token_id:
            self.logger.info(f"Collection: {collection_token_id}")
        if royalties:
            self.logger.info(f"Royalties: {len(royalties)} recipients")
        
        # Validate royalties
        if royalties:
            self._validate_royalties(royalties)
        
        # Build NFT metadata
        nft_metadata = self._build_nft_metadata(
            name, description, image_url, collection_token_id,
            royalties, traits, additional_metadata
        )
        
        if self.dry_run:
            # Dry run mode
            tx_data = self._build_nft_creation_transaction(nft_metadata)
            self._log_dry_run_nft_creation(tx_data, name, collection_token_id)
            return "dry_run_nft_creation"
        else:
            # Real transaction
            return self._execute_nft_creation(nft_metadata)
    
    def mint_nft_collection(
        self,
        collection_config: Union[str, Path, Dict[str, Any]]
    ) -> List[str]:
        """
        Mint an entire NFT collection sequentially.
        
        Args:
            collection_config: Path to YAML config file or config dict
            
        Returns:
            List of transaction IDs (one per NFT)
            
        Example config:
            collection:
              token_id: "abc123..."  # Existing collection token
              base_metadata:
                description: "Digital artwork collection"
                
            nfts:
              - name: "Art #1"
                image_url: "https://example.com/1.png"
                traits:
                  properties:
                    background: "blue"
                  levels:
                    rarity: 
                      value: 85
                      max: 100
        """
        if isinstance(collection_config, (str, Path)):
            self.logger.info(f"Loading collection config from {collection_config}")
            with open(collection_config, 'r') as f:
                config = yaml.safe_load(f)
        else:
            config = collection_config
        
        collection = config.get('collection', {})
        nfts = config.get('nfts', [])
        
        collection_token_id = collection.get('token_id')
        base_metadata = collection.get('base_metadata', {})
        
        if not nfts:
            raise ValueError("No NFTs specified in configuration")
        
        self.logger.info(f"Minting {len(nfts)} NFTs sequentially")
        if collection_token_id:
            self.logger.info(f"Collection token: {collection_token_id}")
        
        transaction_ids = []
        failed_nfts = []
        
        for i, nft_config in enumerate(nfts):
            try:
                self.logger.info(f"Minting NFT {i+1}/{len(nfts)}: {nft_config.get('name', f'NFT #{i+1}')}")
                
                # Merge base metadata with NFT-specific metadata
                merged_metadata = {**base_metadata, **nft_config}
                
                tx_id = self.mint_nft(
                    name=merged_metadata.get('name', f'NFT #{i+1}'),
                    description=merged_metadata.get('description', ''),
                    image_url=merged_metadata.get('image_url'),
                    collection_token_id=collection_token_id,
                    royalties=merged_metadata.get('royalties'),
                    traits=merged_metadata.get('traits'),
                    additional_metadata=merged_metadata.get('additional_metadata')
                )
                
                transaction_ids.append(tx_id)
                
                # Add delay between transactions in live mode to avoid overwhelming node
                if not self.dry_run and i < len(nfts) - 1:
                    time.sleep(2)
                
            except Exception as e:
                self.logger.error(f"Failed to mint NFT {i+1}: {e}")
                failed_nfts.append({
                    'index': i+1,
                    'name': nft_config.get('name', f'NFT #{i+1}'),
                    'error': str(e)
                })
                
                # Continue with remaining NFTs
                continue
        
        self.logger.info(f"Collection minting completed: {len(transaction_ids)} successful, {len(failed_nfts)} failed")
        
        if failed_nfts:
            self.logger.warning("Failed NFTs:")
            for failed in failed_nfts:
                self.logger.warning(f"  {failed['index']}. {failed['name']}: {failed['error']}")
        
        return transaction_ids
    
    def _build_nft_metadata(
        self,
        name: str,
        description: str,
        image_url: Optional[str] = None,
        collection_token_id: Optional[str] = None,
        royalties: Optional[List[Dict[str, Any]]] = None,
        traits: Optional[Dict[str, Any]] = None,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Build EIP-24 compliant NFT metadata."""
        metadata = {
            'name': name,
            'description': description,
            'decimals': 0,  # NFTs are non-divisible
            'type': 'NFT',
            'standard': 'EIP-24'
        }
        
        if image_url:
            metadata['image_url'] = image_url
        
        if collection_token_id:
            metadata['collection_token_id'] = collection_token_id
        
        if royalties:
            metadata['royalties'] = royalties
        
        if traits:
            metadata['traits'] = traits
        
        if additional_metadata:
            metadata['additional_metadata'] = additional_metadata
        
        return metadata
    
    def _build_nft_creation_transaction(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Build an NFT creation transaction."""
        if not ERGO_LIB_AVAILABLE:
            # Demo mode transaction
            return {
                "type": "nft_creation",
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
            
            # Add NFT creation output
            nft_output = self._create_nft_output(
                sender_address, metadata, self.MIN_BOX_VALUE_NANOERG
            )
            tx_builder.add_output(nft_output)
            
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
            self.logger.error(f"Failed to build NFT creation transaction: {e}")
            raise
    
    def _execute_nft_creation(self, metadata: Dict[str, Any]) -> str:
        """Execute NFT creation."""
        try:
            # Build transaction
            tx_data = self._build_nft_creation_transaction(metadata)
            
            # Sign transaction
            if not tx_data.get("demo_mode", False):
                signed_tx = self.wallet_manager.sign_transaction(tx_data["unsigned_tx"])
            else:
                signed_tx = tx_data
            
            # Broadcast transaction
            tx_id = self.network_manager.broadcast_transaction(signed_tx)
            
            self.logger.info(f"NFT created. Transaction ID: {tx_id}")
            return tx_id
            
        except Exception as e:
            self.logger.error(f"Failed to execute NFT creation: {e}")
            raise
    
    def _create_nft_output(
        self, 
        address: str, 
        metadata: Dict[str, Any], 
        erg_value: int
    ):
        """Create an output containing the NFT."""
        if not ERGO_LIB_AVAILABLE:
            return {
                "address": address,
                "value": erg_value,
                "registers": self._encode_nft_registers(metadata)
            }
        
        # Create actual ergo-lib output
        addr = ergo.Address.from_base58(address)
        value = ergo.BoxValue.from_i64(erg_value)
        
        # Create output builder
        output_builder = ergo.ErgoBoxCandidateBuilder(value, addr)
        
        # Add registers with NFT metadata
        registers = self._encode_nft_registers(metadata)
        for reg_id, reg_value in registers.items():
            output_builder.add_register(reg_id, reg_value)
        
        return output_builder.build()
    
    def _encode_nft_registers(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Encode NFT metadata into EIP-24 compliant registers."""
        registers = {}
        
        # R4: NFT name
        if 'name' in metadata:
            registers['R4'] = metadata['name']
        
        # R5: Royalty information
        if 'royalties' in metadata:
            registers['R5'] = self._encode_royalties(metadata['royalties'])
        
        # R6: Artwork traits
        if 'traits' in metadata:
            registers['R6'] = metadata['traits']
        else:
            # Default traits structure
            registers['R6'] = {
                'properties': {},
                'levels': {},
                'stats': {}
            }
        
        # R7: Collection token ID
        if 'collection_token_id' in metadata:
            registers['R7'] = metadata['collection_token_id']
        
        # R8: Additional metadata
        additional_info = {}
        if 'image_url' in metadata:
            additional_info['image_url'] = metadata['image_url']
        if 'description' in metadata:
            additional_info['description'] = metadata['description']
        if 'additional_metadata' in metadata:
            additional_info.update(metadata['additional_metadata'])
        
        if additional_info:
            registers['R8'] = additional_info
        
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
    
    def _validate_royalties(self, royalties: List[Dict[str, Any]]):
        """Validate royalty structure."""
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
    
    def _log_dry_run_nft_creation(
        self, 
        tx_data: Dict, 
        name: str, 
        collection_token_id: Optional[str]
    ):
        """Log details of a dry-run NFT creation."""
        self.logger.info("=== DRY RUN NFT CREATION ===")
        self.logger.info(f"NFT Name: {name}")
        
        if collection_token_id:
            self.logger.info(f"Collection: {collection_token_id}")
        else:
            self.logger.info("Standalone NFT (no collection)")
        
        metadata = tx_data.get('metadata', {})
        
        if 'royalties' in metadata:
            royalties = metadata['royalties']
            self.logger.info(f"Royalties ({len(royalties)} recipients):")
            for i, royalty in enumerate(royalties):
                self.logger.info(f"  {i+1}. {royalty['address'][:10]}... {royalty['percentage']}%")
        
        if 'traits' in metadata:
            traits = metadata['traits']
            if 'properties' in traits and traits['properties']:
                self.logger.info(f"Properties: {traits['properties']}")
            if 'levels' in traits and traits['levels']:
                self.logger.info(f"Levels: {traits['levels']}")
            if 'stats' in traits and traits['stats']:
                self.logger.info(f"Stats: {traits['stats']}")
        
        self.logger.info(f"Transaction fee: {AmountUtils.nanoerg_to_erg(tx_data['fee_nanoerg'])} ERG")
        self.logger.info(f"Minimum box value: {AmountUtils.nanoerg_to_erg(self.MIN_BOX_VALUE_NANOERG)} ERG")
        
        if not tx_data.get('demo_mode', True):
            self.logger.info(f"Total ERG required: {AmountUtils.nanoerg_to_erg(tx_data['total_erg'])} ERG")
        
        self.logger.info("=== END DRY RUN ===")
    
    def validate_nft_collection_config(self, config_file: Union[str, Path]) -> Dict[str, Any]:
        """
        Validate an NFT collection configuration file.
        
        Args:
            config_file: Path to YAML configuration file
            
        Returns:
            Validation result with summary
        """
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            collection = config.get('collection', {})
            nfts = config.get('nfts', [])
            
            # Validate required fields
            errors = []
            warnings = []
            
            if not nfts:
                errors.append("No NFTs specified")
            
            collection_token_id = collection.get('token_id')
            if collection_token_id and len(collection_token_id) != 64:
                warnings.append("Collection token ID should be 64 characters (valid token ID)")
            
            # Validate each NFT
            for i, nft in enumerate(nfts):
                if not nft.get('name'):
                    errors.append(f"NFT {i+1} missing name")
                
                # Validate royalties if present
                royalties = nft.get('royalties', [])
                if royalties:
                    total_percentage = 0
                    for j, royalty in enumerate(royalties):
                        if 'address' not in royalty:
                            errors.append(f"NFT {i+1} royalty {j+1} missing address")
                        elif not self.wallet_manager.validate_address(royalty['address']):
                            errors.append(f"NFT {i+1} invalid royalty address: {royalty['address']}")
                        
                        if 'percentage' not in royalty:
                            errors.append(f"NFT {i+1} royalty {j+1} missing percentage")
                        elif not 0 <= royalty['percentage'] <= 100:
                            errors.append(f"NFT {i+1} invalid royalty percentage: {royalty['percentage']}")
                        else:
                            total_percentage += royalty['percentage']
                    
                    if total_percentage > 100:
                        errors.append(f"NFT {i+1} total royalty percentage ({total_percentage}%) exceeds 100%")
            
            # Calculate costs
            fee_per_nft = 0.001
            min_erg_per_nft = float(AmountUtils.nanoerg_to_erg(self.MIN_BOX_VALUE_NANOERG))
            cost_per_nft = fee_per_nft + min_erg_per_nft
            total_cost = len(nfts) * cost_per_nft
            
            summary = {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "collection_token_id": collection_token_id,
                "nft_count": len(nfts),
                "sequential_transactions": True,
                "cost_per_nft": cost_per_nft,
                "total_cost": total_cost,
                "estimated_time_minutes": len(nfts) * 0.5  # 30 seconds per NFT
            }
            
            return summary
            
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Failed to parse config file: {e}"],
                "warnings": []
            }
    
    def create_nft_collection_template(self, output_file: Union[str, Path]):
        """Create a template NFT collection configuration YAML file."""
        template = {
            "collection": {
                "token_id": "your_collection_token_id_here",
                "base_metadata": {
                    "description": "A unique digital art collection",
                    "royalties": [
                        {
                            "address": "9fArtistAddressHere...",
                            "percentage": 85
                        },
                        {
                            "address": "9fCharityAddressHere...",
                            "percentage": 15
                        }
                    ]
                }
            },
            "nfts": [
                {
                    "name": "Art #1",
                    "description": "First artwork in collection",
                    "image_url": "https://example.com/art1.png",
                    "traits": {
                        "properties": {
                            "background": "blue",
                            "style": "abstract",
                            "artist": "Jane Doe"
                        },
                        "levels": {
                            "rarity": {
                                "value": 85,
                                "max": 100
                            },
                            "complexity": {
                                "value": 7,
                                "max": 10
                            }
                        },
                        "stats": {
                            "creation_year": 2024,
                            "edition": 1
                        }
                    },
                    "additional_metadata": {
                        "explicit": False,
                        "tags": ["art", "digital", "collectible"]
                    }
                },
                {
                    "name": "Art #2",
                    "description": "Second artwork in collection",
                    "image_url": "https://example.com/art2.png",
                    "traits": {
                        "properties": {
                            "background": "red",
                            "style": "minimalist",
                            "artist": "Jane Doe"
                        },
                        "levels": {
                            "rarity": {
                                "value": 92,
                                "max": 100
                            },
                            "complexity": {
                                "value": 5,
                                "max": 10
                            }
                        },
                        "stats": {
                            "creation_year": 2024,
                            "edition": 2
                        }
                    }
                }
            ]
        }
        
        with open(output_file, 'w') as f:
            yaml.dump(template, f, default_flow_style=False, indent=2)
        
        self.logger.info(f"NFT collection configuration template created: {output_file}")
    
    def get_dry_run_mode(self) -> bool:
        """Check if in dry-run mode."""
        return self.dry_run
    
    def set_dry_run_mode(self, dry_run: bool):
        """Set dry-run mode."""
        self.dry_run = dry_run
        self.logger.info(f"Dry-run mode {'enabled' if dry_run else 'disabled'}")