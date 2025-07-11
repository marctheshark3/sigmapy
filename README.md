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

You'll need Python 3.8+ and the official Ergo Python library:

```bash
pip install ergo-lib-python
```

### Installation

Clone and install SigmaPy:

```bash
git clone https://github.com/ergoplatform/sigmapy.git
cd sigmapy
pip install -e .
```

### Your First Transaction

```python
from sigmapy.examples import SimplePaymentExample

# Create a payment example
example = SimplePaymentExample()

# Run the complete tutorial
example.run_complete_example()
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

1. **Start with Basic Wallet Tutorial** - Learn wallet fundamentals
2. **Try Simple Payment Example** - Send your first transaction
3. **Explore Token Operations** - Work with native tokens
4. **Advanced Examples** - Multi-sig, smart contracts, NFTs
5. **Build Your Own** - Use utilities to create custom applications

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