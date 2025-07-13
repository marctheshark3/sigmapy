#!/usr/bin/env python3
"""
CLI Token Distribution Tool

A simple command-line interface for distributing tokens using SigmaPy.

Usage:
    python cli_token_distribution.py validate config.yaml
    python cli_token_distribution.py distribute config.yaml --dry-run
    python cli_token_distribution.py distribute config.yaml --live
"""

import sys
import os
import argparse
import logging
from pathlib import Path

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


def validate_config(config_file: str):
    """Validate a token distribution configuration file."""
    print(f"🔍 Validating configuration: {config_file}")
    
    # Initialize client in dry-run mode for validation
    client = ErgoClient(dry_run=True)
    
    # Validate configuration
    result = client.validate_distribution_config(config_file)
    
    if result['valid']:
        print("✅ Configuration is valid!")
        
        # Show summary if available
        if 'total_recipients' in result:
            print(f"📊 Summary:")
            print(f"   • Recipients: {result['total_recipients']}")
            print(f"   • Total tokens: {result['total_tokens']:,}")
            print(f"   • Single transaction: ✅")
            print(f"   • Min ERG needed: {result['min_erg_needed']:.6f} ERG")
            print(f"   • Total fees: {result['total_fees']:.6f} ERG")
            print(f"   • Total cost: {result['total_erg_needed']:.6f} ERG")
    else:
        print("❌ Configuration has errors:")
        for error in result['errors']:
            print(f"   • {error}")
        return False
    
    if result.get('warnings'):
        print("⚠️  Warnings:")
        for warning in result['warnings']:
            print(f"   • {warning}")
    
    return True


def distribute_tokens(config_file: str, dry_run: bool = True):
    """Distribute tokens according to configuration."""
    mode = "DRY RUN" if dry_run else "LIVE"
    print(f"🚀 Starting token distribution - {mode} MODE")
    print(f"📄 Configuration: {config_file}")
    
    if not dry_run:
        print("⚠️  LIVE MODE: Real transactions will be created!")
        confirm = input("Type 'YES' to continue: ")
        if confirm != 'YES':
            print("❌ Cancelled by user")
            return False
    
    # Initialize client
    client = ErgoClient(dry_run=dry_run)
    
    # First validate the configuration
    print("\n🔍 Validating configuration...")
    if not validate_config(config_file):
        return False
    
    print(f"\n🎯 Executing distribution...")
    
    try:
        # Execute distribution (single transaction)
        tx_id = client.distribute_tokens(config_file)
        
        print(f"\n✅ Distribution completed successfully!")
        print(f"📋 Transaction created: {tx_id}")
        
        if not dry_run:
            print(f"\n🔗 Monitor your transaction on the Ergo blockchain explorer:")
            print(f"   Mainnet: https://explorer.ergoplatform.com/en/transactions/{tx_id}")
            print(f"   Testnet: https://testnet.ergoplatform.com/en/transactions/{tx_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Distribution failed: {e}")
        return False


def create_template(output_file: str):
    """Create a template configuration file."""
    print(f"📝 Creating template configuration: {output_file}")
    
    client = ErgoClient(dry_run=True)
    client.token_manager.create_distribution_template(output_file)
    
    print(f"✅ Template created successfully!")
    print(f"📄 Edit {output_file} with your token details and recipient addresses")


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description='SigmaPy Token Distribution CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s validate my_distribution.yaml
  %(prog)s distribute my_distribution.yaml --dry-run
  %(prog)s distribute my_distribution.yaml --live
  %(prog)s template new_distribution.yaml
  
Notes:
  • All recipients are processed in a single transaction
  • Token decimals are automatically fetched from the node
  • Use --dry-run to validate before executing live transactions
        """
    )
    
    parser.add_argument('command', choices=['validate', 'distribute', 'template'],
                        help='Command to execute')
    parser.add_argument('file', help='Configuration file path')
    parser.add_argument('--dry-run', action='store_true', default=True,
                        help='Run in dry-run mode (default)')
    parser.add_argument('--live', action='store_true',
                        help='Run in live mode (create real transactions)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Handle dry-run vs live mode
    if args.live:
        dry_run = False
    else:
        dry_run = True
    
    # Execute command
    try:
        if args.command == 'validate':
            success = validate_config(args.file)
        elif args.command == 'distribute':
            success = distribute_tokens(args.file, dry_run)
        elif args.command == 'template':
            create_template(args.file)
            success = True
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