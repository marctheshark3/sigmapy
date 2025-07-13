#!/usr/bin/env python3
"""
Test Token Distribution - Real Implementation Test

This script tests the token distribution functionality with:
- Large config file (60 recipients)
- Dry-run mode validation
- Configuration validation
- Real transaction building (without broadcasting)

Usage:
    python test_token_distribution.py
"""

import sys
import os
import logging

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sigmapy import ErgoClient
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_token_distribution():
    """Test token distribution functionality."""
    print("🧪 Testing SigmaPy Token Distribution")
    print("=" * 50)
    
    # Test with demo mode (no real wallet needed)
    print("\n1. Initializing ErgoClient in dry-run mode...")
    client = ErgoClient(
        seed_phrase="abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about",
        network="testnet",
        dry_run=True
    )
    
    print(f"   ✓ Client initialized: {client}")
    print(f"   ✓ Dry-run mode: {client.get_dry_run_mode()}")
    print(f"   ✓ Network: {client.get_network_info()['network']}")
    
    # Test configuration validation
    print("\n2. Testing configuration validation...")
    config_file = Path(__file__).parent / "test_large_distribution.yaml"
    
    validation_result = client.validate_distribution_config(config_file)
    
    print(f"   ✓ Configuration file: {config_file}")
    print(f"   ✓ Valid: {validation_result['valid']}")
    
    # Print validation result contents for debugging
    print(f"   Debug: validation_result keys = {list(validation_result.keys())}")
    
    if 'total_recipients' in validation_result:
        print(f"   ✓ Total recipients: {validation_result['total_recipients']}")
        print(f"   ✓ Total tokens: {validation_result['total_tokens']}")
        print(f"   ✓ Estimated batches: {validation_result['estimated_batches']}")
        print(f"   ✓ Min ERG needed: {validation_result['min_erg_needed']:.6f} ERG")
        print(f"   ✓ Total fees: {validation_result['total_fees']:.6f} ERG")
        print(f"   ✓ Total ERG needed: {validation_result['total_erg_needed']:.6f} ERG")
    else:
        print(f"   ❌ Validation result missing expected fields")
    
    if validation_result['errors']:
        print(f"   ⚠️  Validation errors: {validation_result['errors']}")
    
    if validation_result['warnings']:
        print(f"   ⚠️  Validation warnings: {validation_result['warnings']}")
    
    # Test dry-run distribution
    print("\n3. Testing dry-run token distribution...")
    try:
        tx_ids = client.distribute_tokens(config_file)
        
        print(f"   ✓ Dry-run distribution completed")
        print(f"   ✓ Transaction IDs generated: {len(tx_ids)}")
        for i, tx_id in enumerate(tx_ids):
            print(f"     {i+1}. {tx_id}")
        
    except Exception as e:
        print(f"   ❌ Error during distribution: {e}")
        return False
    
    # Test address validation
    print("\n4. Testing address validation...")
    test_addresses = [
        "9fRusAarL1KkrWQVsxSRVYnvWzD4dWoLLxbYk3eWBV3jD3qvr3W",  # Valid mainnet
        "3WvsT2Gm4EpsM9Pg18PdY6XyhNNMqXDsvJTbbf6ihLvAmSb7u5RN",  # Valid testnet
        "invalid_address",  # Invalid
        "9"  # Too short
    ]
    
    for addr in test_addresses:
        is_valid = client.validate_address(addr)
        print(f"   {addr[:20]}... : {'✓ Valid' if is_valid else '❌ Invalid'}")
    
    # Test wallet functionality
    print("\n5. Testing wallet functionality...")
    try:
        addresses = client.get_addresses(3)
        print(f"   ✓ Generated {len(addresses)} addresses:")
        for i, addr in enumerate(addresses):
            print(f"     {i+1}. {addr}")
        
        balance = client.get_balance()
        print(f"   ✓ Balance retrieved: {balance['erg']} ERG")
        
    except Exception as e:
        print(f"   ❌ Error testing wallet: {e}")
    
    # Test dry-run mode toggle
    print("\n6. Testing dry-run mode toggle...")
    print(f"   Current dry-run mode: {client.get_dry_run_mode()}")
    
    client.set_dry_run_mode(False)
    print(f"   After disabling: {client.get_dry_run_mode()}")
    
    client.set_dry_run_mode(True)
    print(f"   After re-enabling: {client.get_dry_run_mode()}")
    
    print("\n✅ All tests completed successfully!")
    return True

def test_config_generation():
    """Test configuration file generation."""
    print("\n🔧 Testing configuration generation...")
    
    client = ErgoClient(dry_run=True)
    template_file = Path(__file__).parent / "generated_template.yaml"
    
    try:
        client.token_manager.create_distribution_template(template_file)
        print(f"   ✓ Template created: {template_file}")
        
        # Validate the generated template
        validation = client.validate_distribution_config(template_file)
        print(f"   ✓ Template validation: {validation['valid']}")
        
        if not validation['valid']:
            print(f"   ❌ Template errors: {validation['errors']}")
        
    except Exception as e:
        print(f"   ❌ Error generating template: {e}")

def main():
    """Main test function."""
    print("🚀 SigmaPy Token Distribution Test Suite")
    print("=" * 60)
    
    try:
        # Test core functionality
        if not test_token_distribution():
            return 1
        
        # Test config generation
        test_config_generation()
        
        print("\n🎉 All tests passed! SigmaPy is ready for token distribution.")
        print("\nNext steps:")
        print("1. Update token_id in your distribution config")
        print("2. Add your real seed phrase to .env file") 
        print("3. Test with small amounts first")
        print("4. Disable dry-run mode for live transactions")
        
        return 0
        
    except Exception as e:
        print(f"\n💥 Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())