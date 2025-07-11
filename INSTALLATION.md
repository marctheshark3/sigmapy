# SigmaPy Installation Guide

This guide will walk you through installing SigmaPy and its dependencies, including the required `ergo-lib-python` bindings from the sigma-rust project.

## 🎯 Quick Start

If you just want to try SigmaPy with demo mode (no real blockchain operations):

```bash
git clone https://github.com/ergoplatform/sigmapy.git
cd sigmapy
pip install -e .
python examples/beginner_friendly_demo.py
```

## 📋 Prerequisites

- **Python 3.8+** (Python 3.9+ recommended)
- **Git** for cloning repositories
- **Rust toolchain** (for building ergo-lib-python from source)
- **Virtual environment** (recommended)

## 🔧 Step-by-Step Installation

### 1. Create and Activate Virtual Environment

```bash
# Create virtual environment
python -m venv sigmapy-env

# Activate virtual environment
# On Linux/macOS:
source sigmapy-env/bin/activate

# On Windows:
sigmapy-env\Scripts\activate
```

### 2. Install SigmaPy

```bash
# Clone SigmaPy repository
git clone https://github.com/ergoplatform/sigmapy.git
cd sigmapy

# Install SigmaPy in development mode
pip install -e .
```

### 3. Install ergo-lib-python

The `ergo-lib-python` package provides Python bindings for the Ergo blockchain. There are several ways to install it:

#### Option A: Install from PyPI (Recommended)

```bash
pip install ergo-lib-python
```

**Note**: PyPI packages may not always be up-to-date. If you encounter issues, use Option B.

#### Option B: Build from Source (Latest Features)

If you need the latest features or the PyPI package is outdated:

```bash
# Install Rust toolchain if not already installed
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env

# Install maturin (Python-Rust build tool)
pip install maturin

# Clone sigma-rust repository
git clone https://github.com/ergoplatform/sigma-rust.git
cd sigma-rust

# Navigate to Python bindings directory
cd bindings/ergo-lib-python

# Build and install the bindings
maturin develop --release

# Or build wheel and install
maturin build --release
pip install target/wheels/ergo_lib_python-*.whl
```

#### Option C: Using Pre-built Wheels

Check the [sigma-rust releases page](https://github.com/ergoplatform/sigma-rust/releases) for pre-built wheels:

```bash
# Download and install appropriate wheel for your system
pip install https://github.com/ergoplatform/sigma-rust/releases/download/v0.x.x/ergo_lib_python-0.x.x-*.whl
```

### 4. Verify Installation

```bash
# Test ergo-lib-python installation
python -c "import ergo_lib_python; print('ergo-lib-python installed successfully!')"

# Test SigmaPy installation
python -c "import sigmapy; print('SigmaPy installed successfully!')"
```

## 🚀 Using SigmaPy

### Basic Usage

```python
from sigmapy import ErgoClient

# Initialize client with seed phrase
client = ErgoClient(
    seed_phrase="your twelve word mnemonic phrase goes here for wallet access",
    network="testnet"  # Use "mainnet" for production
)

# Check balance
balance = client.get_balance()
print(f"Balance: {balance['erg']} ERG")

# Get addresses
addresses = client.get_addresses(3)
print(f"Primary address: {addresses[0]}")
```

### Connecting to Ergo Nodes

#### Using Public Nodes (Default)

SigmaPy automatically connects to public nodes:

```python
# Mainnet (default)
client = ErgoClient(seed_phrase="your seed phrase")

# Testnet
client = ErgoClient(seed_phrase="your seed phrase", network="testnet")
```

#### Using Local Node

If you're running a local Ergo node:

```bash
# Start local Ergo node (example)
java -jar ergo-5.0.14.jar --mainnet -c ergo.conf
```

```python
# Connect to local node
client = ErgoClient(
    seed_phrase="your seed phrase",
    node_url="http://localhost:9053",  # Default local node URL
    network="mainnet"
)
```

#### Using Custom Node with API Key

```python
# Connect to custom node with API key
client = ErgoClient(
    seed_phrase="your seed phrase",
    node_url="https://your-custom-node.com",
    api_key="your-api-key",
    network="mainnet"
)
```

### Network Configuration

#### Mainnet Configuration

```python
client = ErgoClient(
    seed_phrase="your seed phrase",
    network="mainnet"
)
```

#### Testnet Configuration

```python
client = ErgoClient(
    seed_phrase="your seed phrase",
    network="testnet"
)
```

## 🎨 Examples

### 1. Mint Your First NFT

```python
from sigmapy import ErgoClient

# Initialize client
client = ErgoClient(seed_phrase="your seed phrase", network="testnet")

# Mint an NFT
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

print(f"NFT minted! Token ID: {nft_id}")
```

### 2. Create and Distribute Tokens

```python
from sigmapy import ErgoClient

client = ErgoClient(seed_phrase="your seed phrase", network="testnet")

# Create a token
token_id = client.create_token(
    name="My Utility Token",
    description="A token for my dApp",
    supply=1000000,
    decimals=2
)

# Distribute to multiple addresses
addresses = [
    "9fRusAarL1KkrWQVsxSRVYnvWzD4dWoLLxbYk3eWBV3jD3qvr3W",
    "9gQqZyxyjAptMbfW1Gydm3qaap11zd6X9DrABTbMBRJLjZhQRCA"
]
amounts = [100, 200]

tx_ids = client.airdrop_tokens(token_id, addresses, amounts)
print(f"Tokens distributed in {len(tx_ids)} transactions")
```

### 3. Batch NFT Collection

Create a configuration file `my_collection.yaml`:

```yaml
collection:
  name: "My Art Collection"
  description: "Digital artwork collection"
  creator: "Your Name"
  
nfts:
  - name: "Art #1"
    description: "First artwork"
    image: "https://example.com/art1.png"
    traits:
      background: "blue"
      rarity: "common"
  - name: "Art #2"
    description: "Second artwork"
    image: "https://example.com/art2.png"
    traits:
      background: "red"
      rarity: "rare"
```

```python
# Mint entire collection
nft_ids = client.mint_nft_collection("my_collection.yaml")
print(f"Minted {len(nft_ids)} NFTs!")
```

### 4. Token Distribution from Config

Create `token_distribution.yaml`:

```yaml
distribution:
  batch_size: 50
  fee_per_tx: 0.001
  
recipients:
  - address: "9fRusAarL1KkrWQVsxSRVYnvWzD4dWoLLxbYk3eWBV3jD3qvr3W"
    amount: 100
  - address: "9gQqZyxyjAptMbfW1Gydm3qaap11zd6X9DrABTbMBRJLjZhQRCA"
    amount: 200
```

```python
# Distribute tokens from config
tx_ids = client.distribute_tokens("your_token_id", "token_distribution.yaml")
print(f"Distribution completed in {len(tx_ids)} transactions")
```

## 🛠️ Development Setup

### For Contributors

```bash
# Clone repository
git clone https://github.com/ergoplatform/sigmapy.git
cd sigmapy

# Create development environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest tests/

# Run linting
black src/
flake8 src/
mypy src/
```

### Building Documentation

```bash
# Install documentation dependencies
pip install -e ".[docs]"

# Build documentation
cd docs/
make html

# View documentation
open _build/html/index.html
```

## 🔍 Troubleshooting

### Common Issues

#### 1. ergo-lib-python Installation Fails

**Error**: `maturin not found` or `rust compiler not found`

**Solution**:
```bash
# Install Rust toolchain
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env

# Install maturin
pip install maturin

# Try building again
cd sigma-rust/bindings/ergo-lib-python
maturin develop --release
```

#### 2. Node Connection Issues

**Error**: `Connection refused` or `Network timeout`

**Solution**:
```python
# Try different public nodes
client = ErgoClient(
    seed_phrase="your seed phrase",
    node_url="https://api.ergoplatform.com",  # Alternative public node
    network="mainnet"
)

# Or use testnet
client = ErgoClient(
    seed_phrase="your seed phrase",
    network="testnet"
)
```

#### 3. Insufficient Balance

**Error**: `Insufficient funds for transaction`

**Solution**:
```python
# Check your balance first
balance = client.get_balance()
print(f"Current balance: {balance['erg']} ERG")

# For testnet, you can get test ERG from faucets
# For mainnet, ensure you have sufficient ERG
```

#### 4. Invalid Address Format

**Error**: `Invalid address format`

**Solution**:
```python
# Validate addresses before using
address = "9fRusAarL1KkrWQVsxSRVYnvWzD4dWoLLxbYk3eWBV3jD3qvr3W"
if client.validate_address(address):
    # Use address
    pass
else:
    print("Invalid address format")
```

### Environment Variables

You can set default configuration using environment variables:

```bash
# Set default network
export SIGMAPY_NETWORK=testnet

# Set default node URL
export SIGMAPY_NODE_URL=http://localhost:9053

# Set API key
export SIGMAPY_API_KEY=your_api_key
```

## 📚 Learning Resources

### Tutorials

1. **Basic Operations**: `python examples/beginner_friendly_demo.py`
2. **Advanced Transactions**: `python examples/advanced_transaction.py`
3. **Configuration Examples**: Check `examples/configs/` directory

### Documentation

- **API Reference**: [SigmaPy Documentation](https://sigmapy.readthedocs.io)
- **Ergo Documentation**: [docs.ergoplatform.org](https://docs.ergoplatform.org)
- **Sigma-Rust**: [GitHub Repository](https://github.com/ergoplatform/sigma-rust)

### Community

- **Discord**: [Ergo Discord](https://discord.gg/ergo)
- **Telegram**: [Ergo Telegram](https://t.me/ergoplatform)
- **Forum**: [Ergo Forum](https://www.ergoforum.org)

## ⚠️ Security Notes

### Seed Phrase Security

- **Never share your seed phrase** with anyone
- **Never commit seed phrases** to version control
- **Use environment variables** for production:

```python
import os
seed_phrase = os.getenv("WALLET_SEED_PHRASE")
client = ErgoClient(seed_phrase=seed_phrase)
```

### Network Security

- **Use HTTPS nodes** in production
- **Validate all addresses** before sending transactions
- **Test on testnet** before mainnet operations

### Transaction Security

- **Always verify transaction details** before signing
- **Use appropriate fees** to ensure timely confirmation
- **Monitor transaction status** until confirmation

## 📝 License

SigmaPy is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📞 Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/ergoplatform/sigmapy/issues)
- **Discord**: Get help from the community
- **Email**: community@ergoplatform.org

---

**Happy building with SigmaPy! 🚀**