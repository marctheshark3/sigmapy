#!/usr/bin/env python3
"""
Secure Setup Demo - Environment Configuration and Security Best Practices

This script demonstrates how to:
1. Set up secure environment configuration
2. Validate security settings
3. Use environment variables for sensitive data
4. Follow security best practices

Usage:
    python secure_setup_demo.py
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sigmapy import ErgoClient
from sigmapy.utils import EnvManager, validate_env_security


def demo_environment_setup():
    """Demonstrate environment setup and configuration."""
    print("🔧 Environment Setup Demo")
    print("=" * 50)
    print()
    
    # Initialize environment manager
    env_manager = EnvManager()
    
    print("1. Checking for .env file...")
    if env_manager.env_file.exists():
        print(f"   ✅ .env file found: {env_manager.env_file}")
        print(f"   📊 Loaded {len(env_manager.loaded_vars)} variables")
    else:
        print(f"   ❌ .env file not found: {env_manager.env_file}")
        print("   🔧 Creating example .env file...")
        
        # Create .env file
        env_manager.create_env_file()
        print(f"   ✅ Created .env.example file")
        print("   💡 Copy .env.example to .env and fill in your values")
    
    print()
    
    # Show current configuration
    print("2. Current configuration:")
    config = env_manager.get_config_dict()
    for key, value in config.items():
        if key == "seed_phrase" and value:
            # Don't show full seed phrase for security
            display_value = f"{value[:20]}..." if len(value) > 20 else "[HIDDEN]"
        elif key == "api_key" and value:
            display_value = f"{value[:8]}..." if len(value) > 8 else "[HIDDEN]"
        else:
            display_value = value
        print(f"   {key}: {display_value}")
    
    print()
    
    # Security validation
    print("3. Security validation:")
    security = validate_env_security()
    
    if security["secure"]:
        print("   ✅ All security checks passed")
    else:
        print("   ❌ Security issues detected:")
        for issue in security["issues"]:
            print(f"      - {issue}")
    
    if security["warnings"]:
        print("   ⚠️  Security warnings:")
        for warning in security["warnings"]:
            print(f"      - {warning}")
    
    print()


def demo_secure_client_initialization():
    """Demonstrate secure client initialization."""
    print("🔐 Secure Client Initialization")
    print("=" * 50)
    print()
    
    print("1. Initializing ErgoClient with environment variables...")
    
    try:
        # Initialize client - will use .env file automatically
        client = ErgoClient()
        
        print("   ✅ ErgoClient initialized successfully")
        print(f"   🌐 Network: {client.get_network_info()['network']}")
        print(f"   📍 Primary address: {client.get_addresses()[0]}")
        
    except ValueError as e:
        print(f"   ❌ Client initialization failed: {e}")
        print("   💡 This is expected if there are security issues")
        print("   💡 Check your .env file configuration")
    
    except Exception as e:
        print(f"   ⚠️  Client initialization error: {e}")
        print("   💡 This may be due to missing ergo-lib-python")
    
    print()


def demo_environment_overrides():
    """Demonstrate how to override environment variables."""
    print("🔄 Environment Variable Overrides")
    print("=" * 50)
    print()
    
    print("1. Using environment variables (default)...")
    try:
        client1 = ErgoClient()
        network1 = client1.get_network_info()['network']
        print(f"   📍 Network from env: {network1}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    print()
    
    print("2. Overriding with explicit parameters...")
    try:
        client2 = ErgoClient(
            network="testnet",
            seed_phrase="abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
        )
        network2 = client2.get_network_info()['network']
        print(f"   📍 Network from params: {network2}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    print()


def demo_security_best_practices():
    """Demonstrate security best practices."""
    print("🛡️  Security Best Practices")
    print("=" * 50)
    print()
    
    print("✅ DO:")
    print("   • Store seed phrases in .env files")
    print("   • Add .env to .gitignore")
    print("   • Use environment variables in production")
    print("   • Validate configuration before use")
    print("   • Use testnet for development")
    print("   • Keep ergo-lib-python updated")
    
    print()
    
    print("❌ DON'T:")
    print("   • Hardcode seed phrases in source code")
    print("   • Commit .env files to version control")
    print("   • Share seed phrases with others")
    print("   • Use test seed phrases on mainnet")
    print("   • Store seed phrases in plain text files")
    print("   • Use the same seed phrase for multiple purposes")
    
    print()
    
    print("💡 Additional Security Tips:")
    print("   • Use different addresses for different purposes")
    print("   • Monitor your transactions regularly")
    print("   • Use multi-signature wallets for large amounts")
    print("   • Keep backups of your seed phrase secure")
    print("   • Test on testnet before mainnet operations")
    
    print()


def demo_environment_file_creation():
    """Demonstrate creating and managing .env files."""
    print("📝 Environment File Management")
    print("=" * 50)
    print()
    
    env_manager = EnvManager()
    
    print("1. Creating .env file template...")
    
    # Create example .env file
    example_path = Path(__file__).parent.parent / ".env.example"
    if example_path.exists():
        print(f"   ✅ .env.example already exists: {example_path}")
    else:
        env_manager.create_env_file()
        print(f"   ✅ Created .env.example: {example_path}")
    
    print()
    
    print("2. .env file template contents:")
    print("   ```")
    print("   # SigmaPy Environment Configuration")
    print("   SIGMAPY_SEED_PHRASE=\"your twelve word mnemonic...\"")
    print("   SIGMAPY_NETWORK=\"testnet\"")
    print("   SIGMAPY_NODE_URL=\"\"")
    print("   SIGMAPY_API_KEY=\"\"")
    print("   SIGMAPY_DEMO_MODE=\"true\"")
    print("   ```")
    
    print()
    
    print("3. To use the .env file:")
    print("   • Copy .env.example to .env")
    print("   • Fill in your actual values")
    print("   • Never commit .env to git")
    print("   • Keep .env file permissions secure")
    
    print()


def main():
    """Run all security demos."""
    print("🔐 SigmaPy Security and Environment Demo")
    print("This demo shows how to securely configure SigmaPy")
    print("using environment variables and .env files.")
    print()
    
    try:
        demo_environment_setup()
        demo_secure_client_initialization()
        demo_environment_overrides()
        demo_security_best_practices()
        demo_environment_file_creation()
        
        print("🎉 Security demo completed successfully!")
        print()
        print("📚 What you learned:")
        print("• How to use .env files for secure configuration")
        print("• How to validate security settings")
        print("• How to override environment variables")
        print("• Security best practices for seed phrases")
        print("• How to create and manage environment files")
        print()
        print("🔧 Next steps:")
        print("• Create your own .env file with real values")
        print("• Test with testnet before using mainnet")
        print("• Review and follow all security best practices")
        print("• Set up proper file permissions for .env")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("💡 Check your environment configuration")


if __name__ == "__main__":
    main()