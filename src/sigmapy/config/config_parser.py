"""
ConfigParser - Configuration file parsing and validation

This module provides utilities for parsing and validating configuration files
used for batch operations and complex workflows.
"""

from typing import Dict, Any, Union
from pathlib import Path
import json
import yaml
import logging


class ConfigParser:
    """
    Parser for configuration files supporting YAML and JSON formats.
    
    This class provides methods to parse, validate, and process configuration
    files for various SigmaPy operations including NFT collections, token
    distributions, and batch operations.
    """
    
    def __init__(self):
        """Initialize ConfigParser."""
        self.logger = logging.getLogger(__name__)
    
    @staticmethod
    def parse_file(config_file: Union[str, Path]) -> Dict[str, Any]:
        """
        Parse a configuration file.
        
        Args:
            config_file: Path to YAML or JSON configuration file
            
        Returns:
            Dictionary containing parsed configuration
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file format is invalid
            
        Examples:
            >>> config = ConfigParser.parse_file("nft_collection.yaml")
            >>> collection_name = config["collection"]["name"]
        """
        config_path = Path(config_file)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        # Determine file format
        if config_path.suffix.lower() in ['.yaml', '.yml']:
            return ConfigParser._parse_yaml(config_path)
        elif config_path.suffix.lower() == '.json':
            return ConfigParser._parse_json(config_path)
        else:
            raise ValueError(f"Unsupported configuration file format: {config_path.suffix}")
    
    @staticmethod
    def _parse_yaml(config_path: Path) -> Dict[str, Any]:
        """Parse YAML configuration file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML format in {config_path}: {e}")
        except Exception as e:
            raise ValueError(f"Failed to parse YAML file {config_path}: {e}")
    
    @staticmethod
    def _parse_json(config_path: Path) -> Dict[str, Any]:
        """Parse JSON configuration file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in {config_path}: {e}")
        except Exception as e:
            raise ValueError(f"Failed to parse JSON file {config_path}: {e}")
    
    @staticmethod
    def validate_nft_collection_config(config: Dict[str, Any]) -> None:
        """
        Validate NFT collection configuration.
        
        Args:
            config: Configuration dictionary
            
        Raises:
            ValueError: If configuration is invalid
            
        Expected format:
            collection:
              name: "Collection Name"
              description: "Collection description"
              creator: "Creator Name"
              
            nfts:
              - name: "NFT #1"
                description: "NFT description"
                image: "image_url"
                traits: {...}
        """
        if not isinstance(config, dict):
            raise ValueError("Configuration must be a dictionary")
        
        # Validate collection section
        if "collection" in config:
            collection = config["collection"]
            if not isinstance(collection, dict):
                raise ValueError("'collection' must be a dictionary")
            
            # Check required fields
            if "name" not in collection:
                raise ValueError("Collection must have a 'name' field")
        
        # Validate nfts section
        if "nfts" not in config:
            raise ValueError("Configuration must contain 'nfts' section")
        
        nfts = config["nfts"]
        if not isinstance(nfts, list) or len(nfts) == 0:
            raise ValueError("'nfts' must be a non-empty list")
        
        # Validate each NFT
        for i, nft in enumerate(nfts):
            if not isinstance(nft, dict):
                raise ValueError(f"NFT {i+1} must be a dictionary")
            
            if "name" not in nft:
                raise ValueError(f"NFT {i+1} must have a 'name' field")
            
            if "description" not in nft:
                raise ValueError(f"NFT {i+1} must have a 'description' field")
            
            # Validate traits if present
            if "traits" in nft and not isinstance(nft["traits"], dict):
                raise ValueError(f"NFT {i+1} traits must be a dictionary")
    
    @staticmethod
    def validate_token_distribution_config(config: Dict[str, Any]) -> None:
        """
        Validate token distribution configuration.
        
        Args:
            config: Configuration dictionary
            
        Raises:
            ValueError: If configuration is invalid
            
        Expected format:
            distribution:
              token_id: "token_id"
              batch_size: 50
              fee_per_tx: 0.001
              
            recipients:
              - address: "9f..."
                amount: 10
              - address: "9g..."
                amount: 20
        """
        if not isinstance(config, dict):
            raise ValueError("Configuration must be a dictionary")
        
        # Validate distribution section (optional)
        if "distribution" in config:
            distribution = config["distribution"]
            if not isinstance(distribution, dict):
                raise ValueError("'distribution' must be a dictionary")
            
            # Validate optional fields
            if "batch_size" in distribution:
                batch_size = distribution["batch_size"]
                if not isinstance(batch_size, int) or batch_size <= 0:
                    raise ValueError("'batch_size' must be a positive integer")
            
            if "fee_per_tx" in distribution:
                fee = distribution["fee_per_tx"]
                if not isinstance(fee, (int, float)) or fee <= 0:
                    raise ValueError("'fee_per_tx' must be a positive number")
        
        # Validate recipients section
        if "recipients" not in config:
            raise ValueError("Configuration must contain 'recipients' section")
        
        recipients = config["recipients"]
        if not isinstance(recipients, list) or len(recipients) == 0:
            raise ValueError("'recipients' must be a non-empty list")
        
        # Validate each recipient
        for i, recipient in enumerate(recipients):
            if not isinstance(recipient, dict):
                raise ValueError(f"Recipient {i+1} must be a dictionary")
            
            if "address" not in recipient:
                raise ValueError(f"Recipient {i+1} must have an 'address' field")
            
            if "amount" not in recipient:
                raise ValueError(f"Recipient {i+1} must have an 'amount' field")
            
            amount = recipient["amount"]
            if not isinstance(amount, (int, float)) or amount <= 0:
                raise ValueError(f"Recipient {i+1} amount must be a positive number")
    
    @staticmethod
    def validate_batch_operation_config(config: Dict[str, Any]) -> None:
        """
        Validate batch operation configuration.
        
        Args:
            config: Configuration dictionary
            
        Raises:
            ValueError: If configuration is invalid
            
        Expected format:
            batch:
              type: "token_distribution" | "nft_collection" | "mixed"
              parallel: true/false
              
            operations:
              - type: "create_token"
                parameters: {...}
              - type: "distribute_tokens"
                parameters: {...}
        """
        if not isinstance(config, dict):
            raise ValueError("Configuration must be a dictionary")
        
        # Validate batch section
        if "batch" not in config:
            raise ValueError("Configuration must contain 'batch' section")
        
        batch = config["batch"]
        if not isinstance(batch, dict):
            raise ValueError("'batch' must be a dictionary")
        
        if "type" not in batch:
            raise ValueError("Batch must have a 'type' field")
        
        valid_types = ["token_distribution", "nft_collection", "mixed"]
        if batch["type"] not in valid_types:
            raise ValueError(f"Batch type must be one of: {valid_types}")
        
        # Validate operations section
        if "operations" not in config:
            raise ValueError("Configuration must contain 'operations' section")
        
        operations = config["operations"]
        if not isinstance(operations, list) or len(operations) == 0:
            raise ValueError("'operations' must be a non-empty list")
        
        # Validate each operation
        for i, operation in enumerate(operations):
            if not isinstance(operation, dict):
                raise ValueError(f"Operation {i+1} must be a dictionary")
            
            if "type" not in operation:
                raise ValueError(f"Operation {i+1} must have a 'type' field")
            
            if "parameters" not in operation:
                raise ValueError(f"Operation {i+1} must have a 'parameters' field")
            
            if not isinstance(operation["parameters"], dict):
                raise ValueError(f"Operation {i+1} parameters must be a dictionary")
    
    @staticmethod
    def get_template_config(template_name: str) -> Dict[str, Any]:
        """
        Get a template configuration.
        
        Args:
            template_name: Name of the template
            
        Returns:
            Dictionary containing template configuration
            
        Examples:
            >>> config = ConfigParser.get_template_config("nft_collection")
            >>> # Returns template for NFT collection configuration
        """
        templates = {
            "nft_collection": {
                "collection": {
                    "name": "My NFT Collection",
                    "description": "A unique collection of digital assets",
                    "creator": "Artist Name",
                    "royalty": 0.05
                },
                "nfts": [
                    {
                        "name": "NFT #1",
                        "description": "First NFT in the collection",
                        "image": "https://example.com/image1.png",
                        "traits": {
                            "background": "blue",
                            "rarity": "common"
                        }
                    },
                    {
                        "name": "NFT #2",
                        "description": "Second NFT in the collection",
                        "image": "https://example.com/image2.png",
                        "traits": {
                            "background": "red",
                            "rarity": "rare"
                        }
                    }
                ]
            },
            
            "token_distribution": {
                "distribution": {
                    "token_id": "your_token_id_here",
                    "batch_size": 50,
                    "fee_per_tx": 0.001
                },
                "recipients": [
                    {
                        "address": "9f...",
                        "amount": 10
                    },
                    {
                        "address": "9g...",
                        "amount": 20
                    }
                ]
            },
            
            "batch_operation": {
                "batch": {
                    "type": "mixed",
                    "parallel": False
                },
                "operations": [
                    {
                        "type": "create_token",
                        "parameters": {
                            "name": "My Token",
                            "description": "A utility token",
                            "supply": 1000000,
                            "decimals": 0
                        }
                    },
                    {
                        "type": "distribute_tokens",
                        "parameters": {
                            "token_id": "token_id_from_previous_operation",
                            "recipients": [
                                {"address": "9f...", "amount": 100},
                                {"address": "9g...", "amount": 200}
                            ]
                        }
                    }
                ]
            }
        }
        
        if template_name not in templates:
            raise ValueError(f"Unknown template: {template_name}")
        
        return templates[template_name]
    
    @staticmethod
    def save_config(config: Dict[str, Any], output_file: Union[str, Path]) -> None:
        """
        Save configuration to file.
        
        Args:
            config: Configuration dictionary to save
            output_file: Output file path
            
        Examples:
            >>> config = {"collection": {"name": "My Collection"}}
            >>> ConfigParser.save_config(config, "my_collection.yaml")
        """
        output_path = Path(output_file)
        
        # Determine format based on extension
        if output_path.suffix.lower() in ['.yaml', '.yml']:
            ConfigParser._save_yaml(config, output_path)
        elif output_path.suffix.lower() == '.json':
            ConfigParser._save_json(config, output_path)
        else:
            raise ValueError(f"Unsupported output format: {output_path.suffix}")
    
    @staticmethod
    def _save_yaml(config: Dict[str, Any], output_path: Path) -> None:
        """Save configuration as YAML."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        except Exception as e:
            raise ValueError(f"Failed to save YAML file {output_path}: {e}")
    
    @staticmethod
    def _save_json(config: Dict[str, Any], output_path: Path) -> None:
        """Save configuration as JSON."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, sort_keys=False)
        except Exception as e:
            raise ValueError(f"Failed to save JSON file {output_path}: {e}")
    
    def __str__(self) -> str:
        """String representation of ConfigParser."""
        return "ConfigParser()"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return "ConfigParser()"