#!/usr/bin/env python3
"""
CLI NFT Collection Tool

A comprehensive command-line interface for EIP-24 compliant NFT collection operations.

Usage:
    python cli_nft_collections.py create-collection config.yaml
    python cli_nft_collections.py mint-collection nfts.yaml --dry-run
    python cli_nft_collections.py mint-nft --name "Art #1" --collection-id "abc123..."
    python cli_nft_collections.py validate-collection config.yaml
"""

import sys
import os
import argparse
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sigmapy import ErgoClient


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def create_collection(config_file: str, dry_run: bool = True):
    """Create a collection token from configuration file."""
    print(f"🎨 Creating collection token from {config_file}")
    mode = "DRY RUN" if dry_run else "LIVE"
    print(f"📄 Mode: {mode}")
    
    if not dry_run:
        print("⚠️  LIVE MODE: Real collection token will be created!")
        confirm = input("Type 'YES' to continue: ")
        if confirm != 'YES':
            print("❌ Cancelled by user")
            return False
    
    # Initialize client
    client = ErgoClient(dry_run=dry_run)
    
    # Validate configuration first
    print("\n🔍 Validating collection configuration...")
    result = client.validate_collection_config(config_file)
    
    if not result['valid']:
        print("❌ Configuration has errors:")
        for error in result['errors']:
            print(f"   • {error}")
        return False
    
    print("✅ Configuration is valid!")
    print(f"📊 Summary:")
    print(f"   • Collection: {result['collection_name']}")
    print(f"   • Supply: {result['supply']:,}")
    print(f"   • Royalty recipients: {result['royalty_count']}")
    print(f"   • Total royalty: {result['total_royalty_percentage']}%")
    print(f"   • Cost: {result['total_cost']:.6f} ERG")
    
    if result.get('warnings'):
        print("⚠️  Warnings:")
        for warning in result['warnings']:
            print(f"   • {warning}")
    
    # Create collection
    print(f"\n🚀 Creating collection token...")
    
    try:
        tx_id = client.create_collection_from_config(config_file)
        
        print(f"\n✅ Collection token created successfully!")
        print(f"📋 Transaction ID: {tx_id}")
        
        if not dry_run:
            print(f"\n🔗 Monitor your transaction on the Ergo blockchain explorer:")
            print(f"   Mainnet: https://explorer.ergoplatform.com/en/transactions/{tx_id}")
            print(f"   Testnet: https://testnet.ergoplatform.com/en/transactions/{tx_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Collection creation failed: {e}")
        return False


def mint_collection(config_file: str, dry_run: bool = True):
    """Mint an entire NFT collection from configuration file."""
    print(f"🎨 Minting NFT collection from {config_file}")
    mode = "DRY RUN" if dry_run else "LIVE"
    print(f"📄 Mode: {mode}")
    
    # Initialize client
    client = ErgoClient(dry_run=dry_run)
    
    # Validate configuration first
    print("\n🔍 Validating NFT collection configuration...")
    result = client.validate_nft_collection_config(config_file)
    
    if not result['valid']:
        print("❌ Configuration has errors:")
        for error in result['errors']:
            print(f"   • {error}")
        return False
    
    print("✅ Configuration is valid!")
    print(f"📊 Summary:")
    print(f"   • NFT count: {result['nft_count']}")
    print(f"   • Sequential transactions: ✅")
    print(f"   • Cost per NFT: {result['cost_per_nft']:.6f} ERG")
    print(f"   • Total cost: {result['total_cost']:.6f} ERG")
    print(f"   • Estimated time: {result['estimated_time_minutes']:.1f} minutes")
    
    if result.get('collection_token_id'):
        print(f"   • Collection: {result['collection_token_id']}")
    
    if result.get('warnings'):
        print("⚠️  Warnings:")
        for warning in result['warnings']:
            print(f"   • {warning}")
    
    if not dry_run:
        print(f"\n⚠️  LIVE MODE: {result['nft_count']} real NFTs will be created!")
        print(f"💰 Total cost: {result['total_cost']:.6f} ERG")
        confirm = input("Type 'YES' to continue: ")
        if confirm != 'YES':
            print("❌ Cancelled by user")
            return False
    
    # Mint collection
    print(f"\n🚀 Minting {result['nft_count']} NFTs...")
    
    try:
        tx_ids = client.mint_nft_collection(config_file)
        
        successful = len([tx for tx in tx_ids if not tx.startswith('dry_run')])
        
        print(f"\n✅ NFT collection minting completed!")
        print(f"📋 Transactions created: {len(tx_ids)}")
        print(f"✅ Successful: {successful}")
        
        if dry_run:
            print("\n🔍 Dry run transactions:")
            for i, tx_id in enumerate(tx_ids, 1):
                print(f"   {i}. {tx_id}")
        else:
            print("\n📋 Transaction IDs:")
            for i, tx_id in enumerate(tx_ids, 1):
                print(f"   {i}. {tx_id}")
            
            print(f"\n🔗 Monitor your transactions on the Ergo blockchain explorer:")
            print(f"   Mainnet: https://explorer.ergoplatform.com/")
            print(f"   Testnet: https://testnet.ergoplatform.com/")
        
        return True
        
    except Exception as e:
        print(f"❌ Collection minting failed: {e}")
        return False


def mint_single_nft(
    name: str,
    description: str = "",
    image_url: Optional[str] = None,
    collection_token_id: Optional[str] = None,
    dry_run: bool = True
):
    """Mint a single NFT."""
    print(f"🎨 Minting single NFT: {name}")
    mode = "DRY RUN" if dry_run else "LIVE"
    print(f"📄 Mode: {mode}")
    
    if not dry_run:
        print("⚠️  LIVE MODE: Real NFT will be created!")
        confirm = input("Type 'YES' to continue: ")
        if confirm != 'YES':
            print("❌ Cancelled by user")
            return False
    
    # Initialize client
    client = ErgoClient(dry_run=dry_run)
    
    print(f"\n🚀 Minting NFT...")
    print(f"   • Name: {name}")
    print(f"   • Description: {description}")
    if image_url:
        print(f"   • Image: {image_url}")
    if collection_token_id:
        print(f"   • Collection: {collection_token_id}")
    
    try:
        tx_id = client.mint_nft(
            name=name,
            description=description,
            image_url=image_url,
            collection_token_id=collection_token_id
        )
        
        print(f"\n✅ NFT minted successfully!")
        print(f"📋 Transaction ID: {tx_id}")
        
        if not dry_run:
            print(f"\n🔗 Monitor your transaction on the Ergo blockchain explorer:")
            print(f"   Mainnet: https://explorer.ergoplatform.com/en/transactions/{tx_id}")
            print(f"   Testnet: https://testnet.ergoplatform.com/en/transactions/{tx_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ NFT minting failed: {e}")
        return False


def validate_collection_config(config_file: str):
    """Validate a collection configuration file."""
    print(f"🔍 Validating collection configuration: {config_file}")
    
    # Initialize client in dry-run mode for validation
    client = ErgoClient(dry_run=True)
    
    # Validate configuration
    result = client.validate_collection_config(config_file)
    
    if result['valid']:
        print("✅ Collection configuration is valid!")
        
        print(f"📊 Summary:")
        print(f"   • Collection: {result['collection_name']}")
        print(f"   • Supply: {result['supply']:,}")
        print(f"   • Royalty recipients: {result['royalty_count']}")
        print(f"   • Total royalty: {result['total_royalty_percentage']}%")
        print(f"   • Transaction fee: {result['transaction_fee']:.6f} ERG")
        print(f"   • Min ERG needed: {result['min_erg_needed']:.6f} ERG")
        print(f"   • Total cost: {result['total_cost']:.6f} ERG")
    else:
        print("❌ Collection configuration has errors:")
        for error in result['errors']:
            print(f"   • {error}")
        return False
    
    if result.get('warnings'):
        print("⚠️  Warnings:")
        for warning in result['warnings']:
            print(f"   • {warning}")
    
    return True


def validate_nft_config(config_file: str):
    """Validate an NFT collection configuration file."""
    print(f"🔍 Validating NFT collection configuration: {config_file}")
    
    # Initialize client in dry-run mode for validation
    client = ErgoClient(dry_run=True)
    
    # Validate configuration
    result = client.validate_nft_collection_config(config_file)
    
    if result['valid']:
        print("✅ NFT collection configuration is valid!")
        
        print(f"📊 Summary:")
        print(f"   • NFT count: {result['nft_count']}")
        print(f"   • Sequential transactions: ✅")
        print(f"   • Cost per NFT: {result['cost_per_nft']:.6f} ERG")
        print(f"   • Total cost: {result['total_cost']:.6f} ERG")
        print(f"   • Estimated time: {result['estimated_time_minutes']:.1f} minutes")
        
        if result.get('collection_token_id'):
            print(f"   • Collection: {result['collection_token_id']}")
    else:
        print("❌ NFT collection configuration has errors:")
        for error in result['errors']:
            print(f"   • {error}")
        return False
    
    if result.get('warnings'):
        print("⚠️  Warnings:")
        for warning in result['warnings']:
            print(f"   • {warning}")
    
    return True


def create_collection_template(output_file: str):
    """Create a template collection configuration file."""
    print(f"📝 Creating collection template: {output_file}")
    
    client = ErgoClient(dry_run=True)
    client.collection_manager.create_collection_template(output_file)
    
    print(f"✅ Collection template created successfully!")
    print(f"📄 Edit {output_file} with your collection details")


def create_nft_template(output_file: str):
    """Create a template NFT collection configuration file."""
    print(f"📝 Creating NFT collection template: {output_file}")
    
    client = ErgoClient(dry_run=True)
    client.nft_minter.create_nft_collection_template(output_file)
    
    print(f"✅ NFT collection template created successfully!")
    print(f"📄 Edit {output_file} with your NFT details and collection token ID")


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description='SigmaPy NFT Collection CLI - EIP-24 Compliant',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Collection operations
  %(prog)s create-collection my_collection.yaml --dry-run
  %(prog)s create-collection my_collection.yaml --live
  %(prog)s validate-collection my_collection.yaml
  %(prog)s collection-template new_collection.yaml

  # NFT operations  
  %(prog)s mint-collection nft_collection.yaml --dry-run
  %(prog)s mint-collection nft_collection.yaml --live
  %(prog)s validate-nfts nft_collection.yaml
  %(prog)s nft-template new_nft_collection.yaml
  
  # Single NFT
  %(prog)s mint-nft --name "Art #1" --description "First artwork"
  %(prog)s mint-nft --name "Art #2" --collection-id "abc123..." --live

Notes:
  • Create collection token first, then use its ID for NFT minting
  • Each NFT requires a separate transaction (Ergo protocol limitation)  
  • Use --dry-run to validate before executing live transactions
  • All operations follow EIP-24 standard for maximum compatibility
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Collection commands
    create_collection_parser = subparsers.add_parser('create-collection', help='Create collection token')
    create_collection_parser.add_argument('config_file', help='Collection configuration file')
    create_collection_parser.add_argument('--dry-run', action='store_true', default=True, help='Run in dry-run mode (default)')
    create_collection_parser.add_argument('--live', action='store_true', help='Run in live mode')
    
    validate_collection_parser = subparsers.add_parser('validate-collection', help='Validate collection config')
    validate_collection_parser.add_argument('config_file', help='Collection configuration file')
    
    collection_template_parser = subparsers.add_parser('collection-template', help='Create collection template')
    collection_template_parser.add_argument('output_file', help='Output template file')
    
    # NFT commands
    mint_collection_parser = subparsers.add_parser('mint-collection', help='Mint NFT collection')
    mint_collection_parser.add_argument('config_file', help='NFT collection configuration file')
    mint_collection_parser.add_argument('--dry-run', action='store_true', default=True, help='Run in dry-run mode (default)')
    mint_collection_parser.add_argument('--live', action='store_true', help='Run in live mode')
    
    validate_nfts_parser = subparsers.add_parser('validate-nfts', help='Validate NFT collection config')
    validate_nfts_parser.add_argument('config_file', help='NFT collection configuration file')
    
    nft_template_parser = subparsers.add_parser('nft-template', help='Create NFT collection template')
    nft_template_parser.add_argument('output_file', help='Output template file')
    
    # Single NFT command
    mint_nft_parser = subparsers.add_parser('mint-nft', help='Mint single NFT')
    mint_nft_parser.add_argument('--name', required=True, help='NFT name')
    mint_nft_parser.add_argument('--description', default='', help='NFT description')
    mint_nft_parser.add_argument('--image-url', help='NFT image URL')
    mint_nft_parser.add_argument('--collection-id', help='Collection token ID')
    mint_nft_parser.add_argument('--dry-run', action='store_true', default=True, help='Run in dry-run mode (default)')
    mint_nft_parser.add_argument('--live', action='store_true', help='Run in live mode')
    
    # Global options
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Handle dry-run vs live mode for applicable commands
    dry_run = True
    if hasattr(args, 'live') and args.live:
        dry_run = False
    elif hasattr(args, 'dry_run'):
        dry_run = args.dry_run
    
    # Execute command
    try:
        success = True
        
        if args.command == 'create-collection':
            success = create_collection(args.config_file, dry_run)
        elif args.command == 'validate-collection':
            success = validate_collection_config(args.config_file)
        elif args.command == 'collection-template':
            create_collection_template(args.output_file)
        elif args.command == 'mint-collection':
            success = mint_collection(args.config_file, dry_run)
        elif args.command == 'validate-nfts':
            success = validate_nft_config(args.config_file)
        elif args.command == 'nft-template':
            create_nft_template(args.output_file)
        elif args.command == 'mint-nft':
            success = mint_single_nft(
                args.name, args.description, args.image_url, 
                args.collection_id, dry_run
            )
        else:
            parser.error(f"Unknown command: {args.command}")
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n❌ Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()