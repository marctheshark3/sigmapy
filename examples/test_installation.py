#!/usr/bin/env python3
"""
Installation Test Script

This script tests if SigmaPy and its dependencies are properly installed.
It checks for all required components and provides helpful error messages.

Usage:
    python test_installation.py
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_python_version():
    """Test if Python version is supported."""
    print("🐍 Testing Python version...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"   ❌ Python {version.major}.{version.minor} is not supported")
        print("   💡 Please upgrade to Python 3.8 or higher")
        return False
    
    print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} is supported")
    return True

def test_sigmapy_import():
    """Test if SigmaPy can be imported."""
    print("📦 Testing SigmaPy import...")
    
    try:
        import sigmapy
        print(f"   ✅ SigmaPy v{sigmapy.__version__} imported successfully")
        return True
    except ImportError as e:
        print(f"   ❌ Failed to import SigmaPy: {e}")
        print("   💡 Try running: pip install -e .")
        return False

def test_sigmapy_components():
    """Test if SigmaPy components can be imported."""
    print("🔧 Testing SigmaPy components...")
    
    components = [
        ("ErgoClient", "sigmapy", "ErgoClient"),
        ("NFTMinter", "sigmapy.operations", "NFTMinter"),
        ("TokenManager", "sigmapy.operations", "TokenManager"),
        ("ConfigParser", "sigmapy.config", "ConfigParser"),
        ("AmountUtils", "sigmapy.utils", "AmountUtils"),
        ("SerializationUtils", "sigmapy.utils", "SerializationUtils"),
    ]
    
    success = True
    for name, module, component in components:
        try:
            mod = __import__(module, fromlist=[component])
            getattr(mod, component)
            print(f"   ✅ {name} imported successfully")
        except ImportError as e:
            print(f"   ❌ Failed to import {name}: {e}")
            success = False
        except AttributeError as e:
            print(f"   ❌ {name} not found in {module}: {e}")
            success = False
    
    return success

def test_ergo_lib_python():
    """Test if ergo-lib-python is available."""
    print("🔗 Testing ergo-lib-python...")
    
    try:
        import ergo_lib_python
        print("   ✅ ergo-lib-python imported successfully")
        print("   🎉 Full blockchain functionality available!")
        return True
    except ImportError:
        print("   ⚠️  ergo-lib-python not found")
        print("   💡 SigmaPy will work in demo mode")
        print("   💡 To enable full functionality, install ergo-lib-python:")
        print("       pip install ergo-lib-python")
        print("   💡 Or build from source:")
        print("       git clone https://github.com/ergoplatform/sigma-rust.git")
        print("       cd sigma-rust/bindings/ergo-lib-python")
        print("       pip install maturin")
        print("       maturin develop --release")
        return False

def test_dependencies():
    """Test if required dependencies are available."""
    print("📚 Testing dependencies...")
    
    dependencies = [
        ("requests", "HTTP client for node communication"),
        ("yaml", "YAML configuration file support"),
        ("json", "JSON support (built-in)"),
        ("typing_extensions", "Enhanced type hints"),
    ]
    
    success = True
    for dep, description in dependencies:
        try:
            if dep == "yaml":
                import yaml
            elif dep == "json":
                import json
            elif dep == "typing_extensions":
                import typing_extensions
            else:
                __import__(dep)
            print(f"   ✅ {dep} - {description}")
        except ImportError:
            print(f"   ❌ {dep} - {description}")
            if dep == "yaml":
                print("       Install with: pip install PyYAML")
            elif dep == "typing_extensions":
                print("       Install with: pip install typing-extensions")
            success = False
    
    return success

def test_basic_functionality():
    """Test basic SigmaPy functionality."""
    print("🧪 Testing basic functionality...")
    
    try:
        from sigmapy import ErgoClient
        
        # Test client initialization (demo mode)
        client = ErgoClient(
            seed_phrase="abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about",
            network="testnet"
        )
        print("   ✅ ErgoClient initialization successful")
        
        # Test utility functions
        nanoerg = client.erg_to_nanoerg(1.5)
        erg = client.nanoerg_to_erg(1500000000)
        print(f"   ✅ Amount conversion: 1.5 ERG = {nanoerg} nanoERG")
        
        # Test address validation
        valid = client.validate_address("9fRusAarL1KkrWQVsxSRVYnvWzD4dWoLLxbYk3eWBV3jD3qvr3W")
        print(f"   ✅ Address validation: {valid}")
        
        # Test balance check (demo mode)
        balance = client.get_balance()
        print(f"   ✅ Balance check: {balance['erg']} ERG (demo mode)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Basic functionality test failed: {e}")
        return False

def test_config_files():
    """Test configuration file functionality."""
    print("📄 Testing configuration files...")
    
    try:
        from sigmapy import ConfigParser
        
        # Test template generation
        nft_template = ConfigParser.get_template_config("nft_collection")
        print("   ✅ NFT collection template generated")
        
        token_template = ConfigParser.get_template_config("token_distribution")
        print("   ✅ Token distribution template generated")
        
        # Test config saving (create temp file)
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_file = f.name
        
        ConfigParser.save_config(nft_template, temp_file)
        print("   ✅ Configuration file saving works")
        
        # Test config loading
        loaded_config = ConfigParser.parse_file(temp_file)
        print("   ✅ Configuration file loading works")
        
        # Clean up
        os.unlink(temp_file)
        
        return True
        
    except Exception as e:
        print(f"   ❌ Configuration test failed: {e}")
        return False

def test_examples():
    """Test if example files exist and can be imported."""
    print("📝 Testing examples...")
    
    examples_dir = Path(__file__).parent
    
    examples = [
        "beginner_friendly_demo.py",
        "advanced_transaction.py",
        "configs/nft_collection.yaml",
        "configs/token_distribution.yaml",
    ]
    
    success = True
    for example in examples:
        example_path = examples_dir / example
        if example_path.exists():
            print(f"   ✅ {example} exists")
        else:
            print(f"   ❌ {example} missing")
            success = False
    
    return success

def main():
    """Run all installation tests."""
    print("🔍 SigmaPy Installation Test")
    print("=" * 50)
    print()
    
    tests = [
        ("Python Version", test_python_version),
        ("SigmaPy Import", test_sigmapy_import),
        ("SigmaPy Components", test_sigmapy_components),
        ("Dependencies", test_dependencies),
        ("ergo-lib-python", test_ergo_lib_python),
        ("Basic Functionality", test_basic_functionality),
        ("Configuration Files", test_config_files),
        ("Examples", test_examples),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            print()
        except Exception as e:
            print(f"   ❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
            print()
    
    # Summary
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10} {test_name}")
        if result:
            passed += 1
    
    print()
    print(f"📈 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! SigmaPy is ready to use.")
        print()
        print("🚀 Next steps:")
        print("   1. Run the demo: python examples/beginner_friendly_demo.py")
        print("   2. Try the tutorials: python -c \"from sigmapy.tutorials import BasicWalletTutorial; BasicWalletTutorial().run_complete_tutorial()\"")
        print("   3. Check the documentation: see README.md and INSTALLATION.md")
    else:
        print("⚠️  Some tests failed. Please check the error messages above.")
        print()
        print("💡 Common solutions:")
        print("   - Install missing dependencies: pip install -r requirements.txt")
        print("   - Install ergo-lib-python: pip install ergo-lib-python")
        print("   - Check Python version: python --version")
        print("   - Reinstall SigmaPy: pip install -e .")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)