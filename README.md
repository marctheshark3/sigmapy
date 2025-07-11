# SigmaPy - Ergo Blockchain Python Tutorials & Examples

**Learn Ergo blockchain development with practical Python examples and step-by-step tutorials.**

SigmaPy is a comprehensive learning resource for developers who want to build on the Ergo blockchain using Python. It provides beginner-friendly tutorials, practical examples, and utility functions that make it easy to understand and implement Ergo blockchain concepts.

## 🎯 What You'll Learn

- **Basic Wallet Operations** - Create, restore, and manage Ergo wallets
- **Transaction Handling** - Send payments, create complex transactions
- **Token Operations** - Work with native tokens and NFTs
- **Smart Contracts** - Interact with ErgoScript contracts
- **Multi-signature Wallets** - Implement collaborative spending
- **Best Practices** - Security, error handling, and optimization

## 🚀 Quick Start

### Prerequisites

You'll need Python 3.8+ and the official Ergo Python library. For complete installation instructions, see [INSTALLATION.md](INSTALLATION.md).

**Quick Demo (No blockchain connection required):**

```bash
git clone https://github.com/ergoplatform/sigmapy.git
cd sigmapy
pip install -e .
python examples/beginner_friendly_demo.py
```

**Full Installation with Blockchain Support:**

```bash
# Install ergo-lib-python
pip install ergo-lib-python

# Or build from source for latest features
git clone https://github.com/ergoplatform/sigma-rust.git
cd sigma-rust/bindings/ergo-lib-python
pip install maturin
maturin develop --release
```

### Your First Transaction

```python
from sigmapy import ErgoClient

# Initialize client with seed phrase
client = ErgoClient(seed_phrase="your seed phrase here")

# Send ERG in one line
tx_id = client.send_erg(recipient="9f...", amount_erg=1.5)

# Mint an NFT in one line
nft_id = client.mint_nft(
    name="My First NFT",
    description="A unique digital asset",
    image_url="https://example.com/image.png"
)
```

## 📚 Tutorials

### 1. Basic Wallet Tutorial
Learn fundamental wallet operations:

```python
from sigmapy.tutorials import BasicWalletTutorial

tutorial = BasicWalletTutorial()
tutorial.run_complete_tutorial()
```

**Covers:**
- Creating new wallets
- Restoring from mnemonic
- Generating addresses
- Checking balances

### 2. Transaction Tutorial
Master transaction creation and management:

```python
from sigmapy.tutorials import TransactionTutorial

tutorial = TransactionTutorial()
tutorial.run_complete_tutorial()
```

**Covers:**
- Building transactions
- Signing and verification
- Fee calculation
- Broadcasting to network

### 3. Token Tutorial
Work with Ergo's native tokens:

```python
from sigmapy.tutorials import TokenTutorial

tutorial = TokenTutorial()
tutorial.run_complete_tutorial()
```

**Covers:**
- Token creation and minting
- Token transfers
- NFT operations
- Token metadata

## 🚀 High-Level APIs

SigmaPy provides beginner-friendly, high-level APIs that make complex operations simple:

### ErgoClient - Your Main Interface

```python
from sigmapy import ErgoClient

# Initialize with seed phrase
client = ErgoClient(seed_phrase="your seed phrase here")

# Or with custom node
client = ErgoClient(
    seed_phrase="your seed phrase here",
    node_url="http://localhost:9053",
    network="testnet"
)
```

### NFT Operations

```python
# Mint a single NFT
nft_id = client.mint_nft(
    name="My Artwork",
    description="A unique piece of digital art",
    image_url="https://example.com/art.png",
    traits={"rarity": "legendary", "color": "gold"}
)

# Mint entire collection from config
nft_ids = client.mint_nft_collection("collection_config.yaml")
```

### Token Operations

```python
# Create a token
token_id = client.create_token(
    name="My Token",
    description="A utility token",
    supply=1000000,
    decimals=2
)

# Distribute to multiple addresses
tx_ids = client.distribute_tokens(
    token_id="abc123...",
    config_file="distribution.yaml"
)

# Airdrop to addresses
tx_ids = client.airdrop_tokens(
    token_id="abc123...",
    addresses=["9f...", "9g...", "9h..."],
    amounts=[100, 200, 300]
)
```

### Configuration-Driven Operations

Create YAML config files for batch operations:

```yaml
# nft_collection.yaml
collection:
  name: "My Art Collection"
  description: "Digital artwork collection"
  
nfts:
  - name: "Art #1"
    description: "First artwork"
    image: "https://example.com/art1.png"
    traits:
      background: "blue"
      rarity: "common"
  # ... more NFTs
```

```yaml
# token_distribution.yaml
distribution:
  batch_size: 50
  fee_per_tx: 0.001
  
recipients:
  - address: "9f..."
    amount: 100
  - address: "9g..."
    amount: 200
  # ... more recipients
```

## 🔧 Examples

### Simple Payment
Send ERG from one address to another:

```python
from sigmapy.examples import SimplePaymentExample

example = SimplePaymentExample()
example.create_payment_transaction(
    sender_address="9f...",
    recipient_address="9g...",
    amount_erg=1.5
)
```

### Token Operations
Create and transfer tokens:

```python
from sigmapy.examples import TokenOperationsExample

example = TokenOperationsExample()
example.create_token(
    name="MyToken",
    description="My first Ergo token",
    amount=1000000
)
```

### Multi-signature Wallet
Collaborative spending with multiple parties:

```python
from sigmapy.examples import MultiSigExample

example = MultiSigExample()
example.create_multisig_wallet(
    required_signatures=2,
    public_keys=["pk1", "pk2", "pk3"]
)
```

## 🛠️ Utilities

SigmaPy includes helpful utilities for common operations:

```python
from sigmapy.utils import AmountUtils, AddressUtils

# Convert between ERG and nanoERG
nanoerg = AmountUtils.erg_to_nanoerg(1.5)
erg = AmountUtils.nanoerg_to_erg(1500000000)

# Validate addresses
is_valid = AddressUtils.validate_address("9f...")
network = AddressUtils.get_network_type("9f...")
```

## 📁 Project Structure

```
sigmapy/
├── src/sigmapy/
│   ├── tutorials/          # Step-by-step learning modules
│   │   ├── basic_wallet.py
│   │   ├── transactions.py
│   │   ├── tokens.py
│   │   └── addresses.py
│   ├── examples/           # Practical code examples
│   │   ├── simple_payment.py
│   │   ├── token_operations.py
│   │   ├── nft_examples.py
│   │   └── multisig_example.py
│   └── utils/              # Helper functions and utilities
│       ├── amount_utils.py
│       ├── address_utils.py
│       ├── transaction_utils.py
│       └── network_utils.py
├── tests/                  # Test suite
├── docs/                   # Documentation
└── examples/               # Standalone example scripts
```

## 🔗 Dependencies

- **ergo-lib-python** - Official Ergo Python bindings
- **requests** - HTTP client for node communication
- **typing-extensions** - Enhanced type hints

## 📖 Learning Path

### For Complete Beginners

1. **Start with the Demo** - Run `python examples/beginner_friendly_demo.py`
2. **Follow Installation Guide** - See [INSTALLATION.md](INSTALLATION.md) for full setup
3. **Try High-Level APIs** - Use `ErgoClient` for simple operations
4. **Explore Config Files** - Use YAML files for batch operations

### For Developers

1. **Basic Wallet Tutorial** - Learn wallet fundamentals
2. **Simple Payment Example** - Send your first transaction
3. **Advanced Transactions** - Multi-output with registers and extensions
4. **Token Operations** - Create and distribute tokens
5. **NFT Collections** - Mint entire collections from config files
6. **Build Your Own** - Use utilities to create custom applications

### Example Commands

```bash
# Run the beginner demo
python examples/beginner_friendly_demo.py

# Run advanced transaction example
python examples/advanced_transaction.py

# Try the basic wallet tutorial
python -c "from sigmapy.tutorials import BasicWalletTutorial; BasicWalletTutorial().run_complete_tutorial()"
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/ergoplatform/sigmapy.git
cd sigmapy

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .[dev]

# Run tests
pytest tests/
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/ergoplatform/sigmapy/issues)
- **Documentation**: [SigmaPy Docs](https://sigmapy.readthedocs.io)
- **Community**: [Ergo Discord](https://discord.gg/ergo)

## 🌟 Acknowledgments

- Built on top of [ergo-lib-python](https://github.com/ergoplatform/sigma-rust/tree/develop/bindings/ergo-lib-python)
- Inspired by the Ergo community's commitment to education
- Special thanks to all contributors and beta testers

---

**Ready to start building on Ergo? Begin with the [Basic Wallet Tutorial](src/sigmapy/tutorials/basic_wallet.py)!**