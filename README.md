# SigmaPy - Production-Ready Ergo Blockchain Python Toolkit

**Build robust Ergo blockchain applications with production-ready Python tooling.**

SigmaPy is a comprehensive Python toolkit for the Ergo blockchain, designed for developers who need reliable, production-ready tools for token distribution, NFT operations, smart contracts, and blockchain automation. It provides both high-level APIs and CLI tools for seamless integration into your applications.

## 🎯 Key Features

- **Production Token Distribution** - Distribute tokens to 60+ recipients in single transactions
- **Node-Agnostic Decimal Support** - Automatic token metadata fetching and decimal handling
- **Dry-Run Validation** - Test transactions before execution
- **CLI Tools** - Ready-to-use command-line interfaces
- **Modular Architecture** - Use standalone tools or integrate into existing applications
- **Real Blockchain Integration** - Built on ergo-lib-python for production use

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Ergo node access (mainnet or testnet)
- Optional: ergo-lib-python for real transactions

### Installation

```bash
git clone https://github.com/ergoplatform/sigmapy.git
cd sigmapy
pip install -e .

# For production use with real transactions
pip install ergo-lib-python
```

### Your First Token Distribution

```bash
# Create a distribution template
python examples/cli_token_distribution.py template my_distribution.yaml

# Edit the template with your token ID and recipients
# Then validate the configuration
python examples/cli_token_distribution.py validate my_distribution.yaml

# Test with dry-run
python examples/cli_token_distribution.py distribute my_distribution.yaml --dry-run

# Execute live (with confirmation)
python examples/cli_token_distribution.py distribute my_distribution.yaml --live
```

## 📊 Token Distribution System

### Single Transaction Processing

SigmaPy processes all recipients in a single transaction, eliminating the need for batching:

- ✅ **60+ recipients in one transaction**
- ✅ **Automatic cost calculation** (0.001 ERG per recipient + single transaction fee)
- ✅ **Production-ready validation**
- ✅ **Comprehensive error handling**

### Configuration Example

```yaml
# token_distribution.yaml
distribution:
  token_id: "1fd6e032e8476c4aa54c18c1a308dce83940e8f4a28f576440513ed7326ad489"
  fee_per_tx: 0.001

recipients:
  - address: "9fRusAarL1KkrWQVsxSRVYnvWzD4dWoLLxbYk3eWBV3jD3qvr3W"
    amount: 100.50    # Fractional amounts supported
    note: "Community leader"
  - address: "9gQqZyxyjAptMbfW1Gydm3qaap11zd6X9DrABTbMBRJLjZhQRCA"
    amount: 250
    note: "Developer contributor"
  # ... up to 60+ recipients
```

### Validation Results

```bash
✅ Configuration is valid!
📊 Summary:
   • Recipients: 60
   • Total tokens: 6,575
   • Single transaction: ✅
   • Min ERG needed: 0.060000 ERG
   • Transaction fee: 0.001000 ERG
   • Total cost: 0.061000 ERG
```

## 🔧 Node-Agnostic Decimal Support

SigmaPy automatically fetches token metadata from Ergo nodes to handle decimals correctly:

```python
from sigmapy import ErgoClient

client = ErgoClient()

# Token decimals are automatically fetched from the node
# Supports fractional amounts based on token's actual decimal places
tx_id = client.distribute_tokens("distribution_with_decimals.yaml")
```

**Decimal Handling Features:**
- ✅ Fetches token info from node automatically
- ✅ Validates fractional amounts against token decimal places
- ✅ Converts between display amounts and smallest units
- ✅ Enhanced logging showing both display and smallest unit amounts
- ✅ Graceful fallback when token info unavailable

## 🛠️ High-Level Python API

### ErgoClient - Your Main Interface

```python
from sigmapy import ErgoClient

# Initialize with environment variables or explicit parameters
client = ErgoClient(
    seed_phrase="your seed phrase here",
    node_url="http://localhost:9053",
    network="mainnet",
    dry_run=True  # Test mode
)

# Validate configuration before execution
result = client.validate_distribution_config("distribution.yaml")
print(f"Valid: {result['valid']}")
print(f"Total cost: {result['total_erg_needed']} ERG")

# Execute distribution (single transaction for all recipients)
tx_id = client.distribute_tokens("distribution.yaml")
print(f"Distribution completed: {tx_id}")
```

### Configuration Validation

```python
# Comprehensive validation with detailed feedback
result = client.validate_distribution_config("my_distribution.yaml")

if result['valid']:
    print(f"✅ Ready to distribute to {result['total_recipients']} recipients")
    print(f"💰 Total cost: {result['total_erg_needed']} ERG")
else:
    for error in result['errors']:
        print(f"❌ {error}")
```

## 📁 CLI Tools

### Token Distribution CLI

Complete command-line interface for token operations:

```bash
# Validate configuration
python examples/cli_token_distribution.py validate config.yaml

# Test with dry-run (shows transaction details without broadcasting)
python examples/cli_token_distribution.py distribute config.yaml --dry-run

# Execute live transactions (requires confirmation)
python examples/cli_token_distribution.py distribute config.yaml --live

# Create template configuration
python examples/cli_token_distribution.py template new_config.yaml

# All recipients processed in single transaction
# Token decimals automatically fetched from node
# Use --dry-run to validate before executing live transactions
```

## 🏗️ Architecture

### Core Components

- **ErgoClient**: High-level API for all blockchain operations
- **WalletManager**: Real ergo-lib-python integration for wallet operations
- **NetworkManager**: Mainnet/testnet node connectivity with fallback support
- **TokenManager**: Production token distribution with decimal support

### File Structure

```
sigmapy/
├── src/sigmapy/
│   ├── client/
│   │   ├── ergo_client.py      # Main API
│   │   ├── wallet_manager.py   # Wallet operations
│   │   └── network_manager.py  # Network connectivity
│   ├── operations/
│   │   └── token_manager.py    # Token distribution system
│   └── utils/                  # Helper utilities
├── examples/
│   ├── cli_token_distribution.py      # Production CLI tool
│   ├── test_large_distribution.yaml   # 60-recipient example
│   └── test_decimal_distribution.yaml # Decimal handling example
└── CLAUDE.md                   # Development guide
```

## 🔄 Production Use Cases

### 1. Recurring Airdrops

Perfect for projects that need to distribute tokens regularly:

```yaml
# Weekly airdrop to 50+ community members
distribution:
  token_id: "your_token_id"
  fee_per_tx: 0.001

recipients:
  # 50+ recipients with varying amounts
  - address: "9f..." 
    amount: 100.25
  # ... more recipients
```

### 2. Token Launch Distribution

Handle initial token distribution efficiently:

- Single transaction for all recipients
- Automatic decimal handling
- Comprehensive validation
- Dry-run testing before launch

### 3. Community Rewards

Distribute rewards based on contribution:

```python
# Load recipients from database/API
recipients = get_contributors_from_api()

# Generate config dynamically
config = create_distribution_config(token_id, recipients)

# Validate and execute
if client.validate_distribution_config(config)['valid']:
    tx_id = client.distribute_tokens(config)
```

## ⚙️ Environment Configuration

```bash
# .env file
ERGO_SEED_PHRASE="your twelve word mnemonic phrase here"
ERGO_NODE_URL="http://127.0.0.1:9053"
ERGO_NETWORK="mainnet"
ERGO_API_KEY="optional_api_key"
```

## 🧪 Testing & Validation

### Dry-Run Mode

Always test before executing live transactions:

```python
# Test mode - builds transactions but doesn't broadcast
client = ErgoClient(dry_run=True)
result = client.distribute_tokens("config.yaml")
print(f"Dry run result: {result}")
```

### Comprehensive Validation

- ✅ Address format validation
- ✅ Token amount validation against decimals
- ✅ Balance checking
- ✅ Fee calculation
- ✅ Transaction size limits

## 🔒 Security Best Practices

- **Never commit seed phrases** - Use environment variables
- **Always use dry-run first** - Test transactions before broadcasting
- **Validate all inputs** - Address formats, amounts, token IDs
- **Monitor wallet balances** - Ensure sufficient funds
- **Use mainnet carefully** - Test on testnet first

## 🛣️ Roadmap

### Phase 1: ✅ Complete - Token Distribution
- Single transaction processing for 60+ recipients
- Node-agnostic decimal support
- CLI tools and validation
- Production-ready error handling

### Phase 2: NFT Operations (Planned)
- NFT minting and batch operations
- Collection management
- Metadata handling

### Phase 3: API Backend (Planned)
- REST API for token operations
- Webhook support
- Database integration

### Phase 4: Storage Rent & Automation (Planned)
- Storage rent collection bots
- Automated UTXO management
- Recurring payment systems

### Phase 5: External Integrations (Planned)
- Nautilus wallet integration
- Rosen bridge support
- DEX integration

## 🤝 Contributing

We welcome contributions! The project follows a modular architecture that makes it easy to add new features.

### Development Setup

```bash
git clone https://github.com/ergoplatform/sigmapy.git
cd sigmapy
python -m venv venv
source venv/bin/activate
pip install -e .[dev]
pytest tests/
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/ergoplatform/sigmapy/issues)
- **Community**: [Ergo Discord](https://discord.gg/ergo)
- **Documentation**: See CLAUDE.md for development guidance

## 🌟 Success Stories

**Token Distribution Achievements:**
- ✅ 60 recipients in single transaction
- ✅ 0.061 ERG total cost (minimal fees)
- ✅ Automatic decimal handling for any token
- ✅ Production-ready validation and error handling
- ✅ CLI tools for easy operation

---

**Ready to distribute tokens at scale? Start with the [CLI tool](examples/cli_token_distribution.py)!**