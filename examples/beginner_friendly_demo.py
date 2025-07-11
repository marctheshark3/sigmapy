#!/usr/bin/env python3
"""
Beginner-Friendly Demo - High-Level SigmaPy API Usage

This script demonstrates the new high-level APIs in SigmaPy that make
common Ergo operations extremely simple for beginners.

Key features demonstrated:
1. Simple client initialization
2. One-line NFT minting
3. Easy token creation and distribution
4. Configuration-driven batch operations
5. Automatic error handling and validation

Usage:
    python beginner_friendly_demo.py
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sigmapy import ErgoClient, ConfigParser
from sigmapy.utils import EnvManager
from pathlib import Path


def demo_simple_operations():
    """Demonstrate simple one-line operations."""
    print("🚀 SigmaPy High-Level API Demo")
    print("=" * 50)
    print()
    
    # Initialize client using environment variables
    print("1. Initializing ErgoClient...")
    
    # Create environment manager to check configuration
    env_manager = EnvManager()
    
    # Check if we have environment configuration
    if env_manager.get_seed_phrase():
        print("   📋 Using configuration from environment variables")
        client = ErgoClient()  # Use env vars
    else:
        print("   ⚠️  No environment configuration found, using demo values")
        print("   💡 Create a .env file with your seed phrase for real operations")
        client = ErgoClient(
            seed_phrase="abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about",
            network="testnet"  # Use testnet for demo
        )
    
    print(f"   ✅ Connected to {client.get_network_info()['network']}")
    print(f"   📍 Primary address: {client.get_addresses()[0]}")
    print()
    
    # Check balance
    print("2. Checking wallet balance...")
    balance = client.get_balance()
    print(f"   💰 ERG Balance: {balance['erg']} ERG")
    print(f"   🪙 Tokens: {len(balance['tokens'])} different tokens")
    print()
    
    # Mint a simple NFT
    print("3. Minting a simple NFT...")
    nft_id = client.mint_nft(
        name="My First NFT",
        description="A unique digital asset created with SigmaPy",
        image_url="https://example.com/my-nft.png",
        traits={
            "rarity": "legendary",
            "color": "gold",
            "created_with": "SigmaPy"
        }
    )
    print(f"   🎨 NFT minted! ID: {nft_id}")
    print()
    
    # Create a token
    print("4. Creating a custom token...")
    token_id = client.create_token(
        name="Demo Token",
        description="A demonstration token created with SigmaPy",
        supply=1000000,
        decimals=2
    )
    print(f"   🪙 Token created! ID: {token_id}")
    print()
    
    # Send some ERG
    print("5. Sending ERG to another address...")
    tx_id = client.send_erg(
        recipient="9gQqZyxyjAptMbfW1Gydm3qaap11zd6X9DrABTbMBRJLjZhQRCA",
        amount_erg=0.1
    )
    print(f"   💸 ERG sent! Transaction ID: {tx_id}")
    print()


def demo_config_driven_operations():
    """Demonstrate configuration-driven operations."""
    print("🔧 Configuration-Driven Operations")
    print("=" * 50)
    print()
    
    # Initialize client using environment variables
    print("Using environment configuration...")
    client = ErgoClient()  # Will use .env file if available
    
    # Get example config directory
    config_dir = Path(__file__).parent / "configs"
    
    # Demo NFT collection minting
    print("1. Minting NFT collection from config...")
    nft_config = config_dir / "nft_collection.yaml"
    
    if nft_config.exists():
        print(f"   📄 Using config: {nft_config}")
        nft_ids = client.mint_nft_collection(nft_config)
        print(f"   🎨 Minted {len(nft_ids)} NFTs from collection!")
        for i, nft_id in enumerate(nft_ids):
            print(f"      NFT #{i+1}: {nft_id}")
    else:
        print(f"   ⚠️  Config file not found: {nft_config}")
        print("   📝 Creating example config...")
        
        # Create example config
        example_config = ConfigParser.get_template_config("nft_collection")
        ConfigParser.save_config(example_config, nft_config)
        print(f"   ✅ Example config created: {nft_config}")
    
    print()
    
    # Demo token distribution
    print("2. Token distribution from config...")
    token_config = config_dir / "token_distribution.yaml"
    
    if token_config.exists():
        print(f"   📄 Using config: {token_config}")
        
        # Create a token first for distribution
        token_id = client.create_token(
            name="Distribution Token",
            description="Token for distribution demo",
            supply=10000
        )
        
        # Distribute tokens
        tx_ids = client.distribute_tokens(token_id, token_config)
        print(f"   🪙 Distributed tokens in {len(tx_ids)} transactions!")
        for i, tx_id in enumerate(tx_ids):
            print(f"      Transaction #{i+1}: {tx_id}")
    else:
        print(f"   ⚠️  Config file not found: {token_config}")
        print("   📝 Creating example config...")
        
        # Create example config
        example_config = ConfigParser.get_template_config("token_distribution")
        ConfigParser.save_config(example_config, token_config)
        print(f"   ✅ Example config created: {token_config}")
    
    print()


def demo_batch_operations():
    """Demonstrate batch operations."""
    print("⚡ Batch Operations")
    print("=" * 50)
    print()
    
    # Initialize client using environment variables
    print("Using environment configuration...")
    client = ErgoClient()  # Will use .env file if available
    
    # Demo airdrop
    print("1. Token airdrop to multiple addresses...")
    
    # Create a token for airdrop
    token_id = client.create_token(
        name="Airdrop Token",
        description="Token for airdrop demo",
        supply=50000
    )
    
    # Define recipients
    recipients = [
        "9fRusAarL1KkrWQVsxSRVYnvWzD4dWoLLxbYk3eWBV3jD3qvr3W",
        "9gQqZyxyjAptMbfW1Gydm3qaap11zd6X9DrABTbMBRJLjZhQRCA",
        "9h8UVJjdUYbNLuSqzZCqKNs2mxjVGYB9JwP4vVtNqmR3sKdxYyZ"
    ]
    
    amounts = [100, 200, 300]  # Different amounts for each recipient
    
    # Execute airdrop
    tx_ids = client.airdrop_tokens(token_id, recipients, amounts)
    print(f"   🪂 Airdropped tokens to {len(recipients)} addresses!")
    print(f"   📦 Completed in {len(tx_ids)} transactions")
    
    print()
    
    # Demo cost estimation
    print("2. Cost estimation for large distribution...")
    
    # Estimate cost for distributing to 100 addresses
    cost_estimate = client.token_manager.estimate_distribution_cost(
        recipient_count=100,
        batch_size=50,
        fee_per_tx=0.001
    )
    
    print(f"   📊 Distribution to 100 addresses:")
    print(f"      Transactions needed: {cost_estimate['transactions']}")
    print(f"      Total fees: {cost_estimate['total_fees']} ERG")
    print(f"      Min box values: {cost_estimate['min_box_values']} ERG")
    print(f"      Total cost: {cost_estimate['total_cost']} ERG")
    
    print()


def demo_utility_functions():
    """Demonstrate utility functions."""
    print("🛠️ Utility Functions")
    print("=" * 50)
    print()
    
    # Initialize client using environment variables
    print("Using environment configuration...")
    client = ErgoClient()  # Will use .env file if available
    
    # Demo conversions
    print("1. Amount conversions...")
    erg_amount = 1.5
    nanoerg_amount = client.erg_to_nanoerg(erg_amount)
    back_to_erg = client.nanoerg_to_erg(nanoerg_amount)
    
    print(f"   💰 {erg_amount} ERG = {nanoerg_amount} nanoERG")
    print(f"   💰 {nanoerg_amount} nanoERG = {back_to_erg} ERG")
    print()
    
    # Demo address validation
    print("2. Address validation...")
    test_addresses = [
        "9fRusAarL1KkrWQVsxSRVYnvWzD4dWoLLxbYk3eWBV3jD3qvr3W",  # Valid
        "invalid_address",  # Invalid
        "9gQqZyxyjAptMbfW1Gydm3qaap11zd6X9DrABTbMBRJLjZhQRCA"   # Valid
    ]
    
    for addr in test_addresses:
        is_valid = client.validate_address(addr)
        status = "✅ Valid" if is_valid else "❌ Invalid"
        print(f"   {status}: {addr[:20]}...")
    
    print()
    
    # Demo network info
    print("3. Network information...")
    network_info = client.get_network_info()
    print(f"   🌐 Network: {network_info['network']}")
    print(f"   🏢 Node: {network_info['node_url']}")
    print(f"   📊 Block height: {network_info['height']}")
    print(f"   🤝 Peers: {network_info['peers']}")
    
    print()


def main():
    """Run all demos."""
    print("🎓 SigmaPy Beginner-Friendly Demo")
    print("This demo showcases the new high-level APIs that make")
    print("Ergo blockchain development accessible to beginners.")
    print()
    
    # Check environment setup
    env_manager = EnvManager()
    print("🔍 Environment Setup Check:")
    
    if env_manager.env_file.exists():
        print(f"   ✅ .env file found: {env_manager.env_file}")
    else:
        print(f"   ⚠️  .env file not found: {env_manager.env_file}")
        print("   💡 Create a .env file for secure configuration")
        print("   📄 See .env.example for template")
    
    # Security validation
    security = env_manager.validate_security()
    if security["secure"]:
        print("   🔐 Security: All checks passed")
    else:
        print("   ⚠️  Security: Issues detected")
        for issue in security["issues"]:
            print(f"       - {issue}")
    
    print()
    
    try:
        # Run all demo sections
        demo_simple_operations()
        demo_config_driven_operations()
        demo_batch_operations()
        demo_utility_functions()
        
        print("🎉 Demo completed successfully!")
        print()
        print("📚 What you learned:")
        print("• How to initialize ErgoClient with environment variables")
        print("• How to mint NFTs with just one line of code")
        print("• How to create and distribute tokens easily")
        print("• How to use configuration files for batch operations")
        print("• How to perform airdrops and cost estimations")
        print("• How to use utility functions for common tasks")
        print("• How to secure your seed phrase using .env files")
        print()
        print("🔧 Next steps:")
        print("• Create a .env file with your seed phrase (see .env.example)")
        print("• Install ergo-lib-python to connect to real nodes")
        print("• Try modifying the configuration files")
        print("• Explore the tutorial modules for deeper learning")
        print("• Build your own applications using these APIs")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("💡 This is expected if ergo-lib-python is not installed.")
        print("   The demo shows how the APIs work conceptually.")
        print("💡 Create a .env file for secure configuration.")


if __name__ == "__main__":
    main()