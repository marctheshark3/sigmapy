"""
NFTMinter - Simplified NFT creation and management

This class provides easy-to-use methods for:
- Single NFT minting
- Batch NFT collection minting
- NFT metadata management
- IPFS integration for images
"""

from typing import Dict, List, Optional, Any, Union
import json
import logging
from pathlib import Path
from dataclasses import dataclass

from ..utils import AmountUtils, SerializationUtils
from ..config import ConfigParser


@dataclass
class NFTMetadata:
    """NFT metadata structure."""
    name: str
    description: str
    image_url: Optional[str] = None
    traits: Optional[Dict[str, Any]] = None
    collection: Optional[str] = None
    creator: Optional[str] = None
    royalty: Optional[float] = None


class NFTMinter:
    """
    Simplified NFT minting operations.
    
    This class provides beginner-friendly methods for creating NFTs
    with automatic metadata serialization and register management.
    """
    
    def __init__(self, wallet_manager, network_manager):
        """
        Initialize NFTMinter.
        
        Args:
            wallet_manager: WalletManager instance for signing
            network_manager: NetworkManager instance for broadcasting
        """
        self.wallet_manager = wallet_manager
        self.network_manager = network_manager
        self.logger = logging.getLogger(__name__)
    
    def mint_single_nft(
        self,
        name: str,
        description: str,
        image_url: Optional[str] = None,
        traits: Optional[Dict[str, Any]] = None,
        collection: Optional[str] = None,
        recipient: Optional[str] = None,
        royalty: Optional[float] = None
    ) -> str:
        """
        Mint a single NFT.
        
        Args:
            name: NFT name
            description: NFT description
            image_url: URL to NFT image
            traits: Dictionary of NFT traits/attributes
            collection: Collection name
            recipient: Address to receive NFT (uses default if None)
            royalty: Royalty percentage (0.0-1.0)
            
        Returns:
            NFT token ID
            
        Examples:
            >>> nft_id = minter.mint_single_nft(
            ...     name="My First NFT",
            ...     description="A unique digital asset",
            ...     image_url="https://example.com/image.png",
            ...     traits={"rarity": "rare", "color": "blue"}
            ... )
        """
        self.logger.info(f"Minting NFT: {name}")
        
        # Create metadata
        metadata = NFTMetadata(
            name=name,
            description=description,
            image_url=image_url,
            traits=traits,
            collection=collection,
            royalty=royalty
        )
        
        # Get recipient address
        if recipient is None:
            recipient = self.wallet_manager.get_primary_address()
        
        # Build NFT transaction
        tx_data = self._build_nft_transaction(metadata, recipient)
        
        # Sign and broadcast
        signed_tx = self.wallet_manager.sign_transaction(tx_data)
        tx_id = self.network_manager.broadcast_transaction(signed_tx)
        
        self.logger.info(f"NFT minted successfully. Transaction ID: {tx_id}")
        return tx_id
    
    def mint_collection(self, config_file: Union[str, Path]) -> List[str]:
        """
        Mint a collection of NFTs from a configuration file.
        
        Args:
            config_file: Path to YAML/JSON configuration file
            
        Returns:
            List of NFT token IDs
            
        Config file format:
            collection:
              name: "My NFT Collection"
              description: "A collection of unique digital assets"
              creator: "Artist Name"
              royalty: 0.05
              
            nfts:
              - name: "NFT #1"
                description: "First NFT"
                image: "ipfs://..."
                traits:
                  background: "blue"
                  rarity: "common"
              - name: "NFT #2"
                description: "Second NFT"
                # ... more NFTs
        """
        self.logger.info(f"Minting NFT collection from {config_file}")
        
        # Parse configuration
        config = ConfigParser.parse_file(config_file)
        
        # Validate configuration
        self._validate_collection_config(config)
        
        # Get collection metadata
        collection_info = config.get("collection", {})
        nfts = config.get("nfts", [])
        
        # Mint each NFT
        token_ids = []
        for i, nft_config in enumerate(nfts):
            try:
                self.logger.info(f"Minting NFT {i+1}/{len(nfts)}: {nft_config.get('name', 'Unnamed')}")
                
                # Merge collection info with NFT config
                merged_config = {**collection_info, **nft_config}
                
                token_id = self.mint_single_nft(
                    name=merged_config.get("name", f"NFT #{i+1}"),
                    description=merged_config.get("description", ""),
                    image_url=merged_config.get("image"),
                    traits=merged_config.get("traits"),
                    collection=collection_info.get("name"),
                    royalty=merged_config.get("royalty")
                )
                
                token_ids.append(token_id)
                
            except Exception as e:
                self.logger.error(f"Failed to mint NFT {i+1}: {e}")
                continue
        
        self.logger.info(f"Collection minting completed. Minted {len(token_ids)} NFTs")
        return token_ids
    
    def mint_nft_with_custom_registers(
        self,
        name: str,
        description: str,
        custom_registers: Dict[str, Any],
        recipient: Optional[str] = None
    ) -> str:
        """
        Mint an NFT with custom register data.
        
        Args:
            name: NFT name
            description: NFT description
            custom_registers: Custom register data (R4-R9)
            recipient: Address to receive NFT
            
        Returns:
            NFT token ID
            
        Examples:
            >>> nft_id = minter.mint_nft_with_custom_registers(
            ...     name="Custom NFT",
            ...     description="NFT with custom data",
            ...     custom_registers={
            ...         "R4": {"type": "String", "value": "Custom data"},
            ...         "R5": {"type": "Int", "value": 12345}
            ...     }
            ... )
        """
        self.logger.info(f"Minting NFT with custom registers: {name}")
        
        # Get recipient address
        if recipient is None:
            recipient = self.wallet_manager.get_primary_address()
        
        # Build transaction with custom registers
        tx_data = self._build_custom_nft_transaction(
            name, description, custom_registers, recipient
        )
        
        # Sign and broadcast
        signed_tx = self.wallet_manager.sign_transaction(tx_data)
        tx_id = self.network_manager.broadcast_transaction(signed_tx)
        
        self.logger.info(f"Custom NFT minted successfully. Transaction ID: {tx_id}")
        return tx_id
    
    def _build_nft_transaction(
        self,
        metadata: NFTMetadata,
        recipient: str
    ) -> Dict[str, Any]:
        """Build NFT transaction with proper metadata serialization."""
        
        # Serialize metadata to registers
        registers = self._serialize_nft_metadata(metadata)
        
        # Create NFT output
        nft_output = {
            "recipient": recipient,
            "value": AmountUtils.erg_to_nanoerg(0.001),  # Minimum box value
            "tokens": [
                {
                    "id": "NFT_TOKEN_ID",  # This would be generated
                    "amount": 1
                }
            ],
            "registers": registers
        }
        
        # Build transaction
        transaction = self.wallet_manager.create_transaction(
            outputs=[nft_output],
            fee_erg=0.001
        )
        
        return transaction
    
    def _build_custom_nft_transaction(
        self,
        name: str,
        description: str,
        custom_registers: Dict[str, Any],
        recipient: str
    ) -> Dict[str, Any]:
        """Build NFT transaction with custom register data."""
        
        # Serialize custom registers
        registers = {}
        for reg_id, reg_data in custom_registers.items():
            registers[reg_id] = SerializationUtils.serialize_for_register(
                reg_id, reg_data["value"], reg_data["type"]
            )
        
        # Add standard NFT metadata if not present
        if "R4" not in registers:
            registers["R4"] = SerializationUtils.serialize_for_register("R4", name, "String")
        if "R5" not in registers:
            registers["R5"] = SerializationUtils.serialize_for_register("R5", description, "String")
        
        # Create NFT output
        nft_output = {
            "recipient": recipient,
            "value": AmountUtils.erg_to_nanoerg(0.001),
            "tokens": [
                {
                    "id": "NFT_TOKEN_ID",
                    "amount": 1
                }
            ],
            "registers": registers
        }
        
        # Build transaction
        transaction = self.wallet_manager.create_transaction(
            outputs=[nft_output],
            fee_erg=0.001
        )
        
        return transaction
    
    def _serialize_nft_metadata(self, metadata: NFTMetadata) -> Dict[str, str]:
        """Serialize NFT metadata to register format."""
        registers = {}
        
        # R4: Name
        registers["R4"] = SerializationUtils.serialize_for_register("R4", metadata.name, "String")
        
        # R5: Description
        registers["R5"] = SerializationUtils.serialize_for_register("R5", metadata.description, "String")
        
        # R6: Image URL (if provided)
        if metadata.image_url:
            registers["R6"] = SerializationUtils.serialize_for_register("R6", metadata.image_url, "String")
        
        # R7: Traits (as JSON if provided)
        if metadata.traits:
            registers["R7"] = SerializationUtils.serialize_for_register("R7", metadata.traits, "JSON")
        
        # R8: Collection info (if provided)
        if metadata.collection:
            collection_data = {
                "name": metadata.collection,
                "creator": metadata.creator,
                "royalty": metadata.royalty
            }
            registers["R8"] = SerializationUtils.serialize_for_register("R8", collection_data, "JSON")
        
        return registers
    
    def _validate_collection_config(self, config: Dict[str, Any]) -> None:
        """Validate NFT collection configuration."""
        if "nfts" not in config:
            raise ValueError("Configuration must contain 'nfts' section")
        
        nfts = config["nfts"]
        if not isinstance(nfts, list) or len(nfts) == 0:
            raise ValueError("'nfts' must be a non-empty list")
        
        for i, nft in enumerate(nfts):
            if not isinstance(nft, dict):
                raise ValueError(f"NFT {i+1} must be a dictionary")
            
            if "name" not in nft:
                raise ValueError(f"NFT {i+1} must have a 'name' field")
    
    def get_nft_metadata(self, token_id: str) -> Dict[str, Any]:
        """
        Get NFT metadata from blockchain.
        
        Args:
            token_id: NFT token ID
            
        Returns:
            Dictionary containing NFT metadata
        """
        try:
            # Get token info from network
            token_info = self.network_manager.get_token_info(token_id)
            
            # Extract metadata from registers
            metadata = self._extract_nft_metadata(token_info)
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Failed to get NFT metadata: {e}")
            return {
                "id": token_id,
                "name": "Unknown NFT",
                "description": "",
                "error": str(e)
            }
    
    def _extract_nft_metadata(self, token_info: Dict[str, Any]) -> Dict[str, Any]:
        """Extract NFT metadata from token info."""
        metadata = {
            "id": token_info.get("id", ""),
            "name": "Unknown NFT",
            "description": "",
            "image_url": None,
            "traits": None,
            "collection": None
        }
        
        # Extract from registers if available
        registers = token_info.get("registers", {})
        
        # R4: Name
        if "R4" in registers:
            try:
                metadata["name"] = self._deserialize_string(registers["R4"])
            except Exception:
                pass
        
        # R5: Description
        if "R5" in registers:
            try:
                metadata["description"] = self._deserialize_string(registers["R5"])
            except Exception:
                pass
        
        # R6: Image URL
        if "R6" in registers:
            try:
                metadata["image_url"] = self._deserialize_string(registers["R6"])
            except Exception:
                pass
        
        # R7: Traits
        if "R7" in registers:
            try:
                metadata["traits"] = self._deserialize_json(registers["R7"])
            except Exception:
                pass
        
        # R8: Collection info
        if "R8" in registers:
            try:
                metadata["collection"] = self._deserialize_json(registers["R8"])
            except Exception:
                pass
        
        return metadata
    
    def _deserialize_string(self, hex_data: str) -> str:
        """Deserialize hex string to text."""
        try:
            # Remove type prefix and decode
            data_bytes = bytes.fromhex(hex_data[4:])  # Skip type prefix
            return data_bytes.decode('utf-8')
        except Exception:
            return ""
    
    def _deserialize_json(self, hex_data: str) -> Dict[str, Any]:
        """Deserialize hex string to JSON."""
        try:
            # Remove type prefix and decode
            data_bytes = bytes.fromhex(hex_data[4:])  # Skip type prefix
            json_string = data_bytes.decode('utf-8')
            return json.loads(json_string)
        except Exception:
            return {}
    
    def __str__(self) -> str:
        """String representation of NFTMinter."""
        return "NFTMinter()"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"NFTMinter(network={self.network_manager.network})"