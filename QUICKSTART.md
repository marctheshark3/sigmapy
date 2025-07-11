# SigmaPy Quick Start Guide

Get up and running with SigmaPy in minutes! This guide will help you start building on Ergo blockchain using Python.

## ⚡ 5-Minute Setup

### 1. Install SigmaPy

```bash
# Clone the repository
git clone https://github.com/ergoplatform/sigmapy.git
cd sigmapy

# Install in development mode
pip install -e .

# Run the demo (works without ergo-lib-python)
python examples/beginner_friendly_demo.py
```

### 2. Install ergo-lib-python (For Real Blockchain Operations)

```bash
# Option 1: Install from PyPI (recommended)
pip install ergo-lib-python

# Option 2: Build from source (latest features)
pip install maturin
git clone https://github.com/ergoplatform/sigma-rust.git
cd sigma-rust/bindings/ergo-lib-python
maturin develop --release
```

### 3. Your First Transaction

```python
from sigmapy import ErgoClient

# Initialize client (replace with your seed phrase)
client = ErgoClient(
    seed_phrase="your twelve word seed phrase goes here",
    network="testnet"  # Use testnet for learning
)

# Check balance
balance = client.get_balance()
print(f"Balance: {balance['erg']} ERG")

# Send ERG
tx_id = client.send_erg(
    recipient="9gQqZyxyjAptMbfW1Gydm3qaap11zd6X9DrABTbMBRJLjZhQRCA",
    amount_erg=0.1
)
print(f"Transaction sent: {tx_id}")
```

## 🎨 Common Operations

### Mint an NFT

```python
nft_id = client.mint_nft(
    name="My First NFT",
    description="A unique digital asset",
    image_url="https://example.com/image.png",
    traits={"rarity": "legendary", "color": "gold"}
)
print(f"NFT minted: {nft_id}")
```

### Create and Distribute Tokens

```python
# Create token
token_id = client.create_token(
    name="My Token",
    description="A utility token",
    supply=1000000,
    decimals=2
)

# Airdrop to multiple addresses
addresses = ["9f...", "9g...", "9h..."]
amounts = [100, 200, 300]
tx_ids = client.airdrop_tokens(token_id, addresses, amounts)
print(f"Airdrop completed: {len(tx_ids)} transactions")
```

### Batch Operations with Config Files

Create `nft_collection.yaml`:
```yaml
collection:
  name: "My Art Collection"
  description: "Digital artwork"
  
nfts:
  - name: "Art #1"
    description: "First artwork"
    image: "https://example.com/art1.png"
    traits: {rarity: "rare"}
  - name: "Art #2"
    description: "Second artwork"
    image: "https://example.com/art2.png"
    traits: {rarity: "common"}
```

```python
# Mint entire collection
nft_ids = client.mint_nft_collection("nft_collection.yaml")
print(f"Minted {len(nft_ids)} NFTs!")
```

## 🔧 Network Configuration

### Using Different Networks

```python
# Testnet (recommended for learning)
client = ErgoClient(
    seed_phrase="your seed phrase",
    network="testnet"
)

# Mainnet (for production)
client = ErgoClient(
    seed_phrase="your seed phrase",
    network="mainnet"
)
```

### Custom Node Configuration

```python
# Local node
client = ErgoClient(
    seed_phrase="your seed phrase",
    node_url="http://localhost:9053",
    network="mainnet"
)

# Custom node with API key
client = ErgoClient(
    seed_phrase="your seed phrase",
    node_url="https://your-node.com",
    api_key="your-api-key",
    network="mainnet"
)
```

## 📊 Monitoring and Utilities

### Check Transaction Status

```python
# Get transaction status
status = client.get_transaction_status("your_tx_id")
print(f"Status: {status['status']}")
print(f"Confirmations: {status['confirmations']}")

# Wait for confirmation
final_status = client.wait_for_confirmation("your_tx_id")
print(f"Transaction confirmed in block {final_status['block_height']}")
```

### Amount Conversions

```python
# Convert ERG to nanoERG
nanoerg = client.erg_to_nanoerg(1.5)  # 1500000000

# Convert nanoERG to ERG
erg = client.nanoerg_to_erg(1500000000)  # 1.5
```

### Address Validation

```python
# Validate addresses
valid = client.validate_address("9f...")
print(f"Address valid: {valid}")
```

## 🔍 Examples and Templates

### Run Built-in Examples

```bash
# Beginner-friendly demo
python examples/beginner_friendly_demo.py

# Advanced transaction example
python examples/advanced_transaction.py

# Basic wallet tutorial
python -c "from sigmapy.tutorials import BasicWalletTutorial; BasicWalletTutorial().run_complete_tutorial()"
```

### Generate Config Templates

```python
from sigmapy import ConfigParser

# Generate NFT collection template
config = ConfigParser.get_template_config("nft_collection")
ConfigParser.save_config(config, "my_collection.yaml")

# Generate token distribution template
config = ConfigParser.get_template_config("token_distribution")
ConfigParser.save_config(config, "my_distribution.yaml")
```

## 🚨 Common Issues and Solutions

### 1. "ergo-lib-python not found"

```bash
# Install ergo-lib-python
pip install ergo-lib-python

# If that fails, build from source
pip install maturin
git clone https://github.com/ergoplatform/sigma-rust.git
cd sigma-rust/bindings/ergo-lib-python
maturin develop --release
```

### 2. "Connection refused" or Network errors

```python
# Try testnet
client = ErgoClient(seed_phrase="your seed phrase", network="testnet")

# Or use different public node
client = ErgoClient(
    seed_phrase="your seed phrase",
    node_url="https://api.ergoplatform.com",
    network="mainnet"
)
```

### 3. "Insufficient funds"

```python
# Check balance first
balance = client.get_balance()
print(f"Available: {balance['erg']} ERG")

# For testnet, get test ERG from faucets
# For mainnet, ensure sufficient ERG balance
```

## 🛡️ Security Best Practices

### Seed Phrase Security

```python
import os

# Use environment variables
seed_phrase = os.getenv("WALLET_SEED_PHRASE")
client = ErgoClient(seed_phrase=seed_phrase)

# Never hardcode seed phrases in your code!
```

### Transaction Verification

```python
# Always verify transaction details
print(f"Sending {amount_erg} ERG to {recipient}")
print("Press Enter to confirm...")
input()

# Send transaction
tx_id = client.send_erg(recipient, amount_erg)
```

## 📚 Next Steps

1. **Explore Examples**: Check the `examples/` directory for more use cases
2. **Read Documentation**: See [INSTALLATION.md](INSTALLATION.md) for detailed setup
3. **Join Community**: Connect with other developers on [Discord](https://discord.gg/ergo)
4. **Build Something**: Create your own dApp using SigmaPy's tools

## 🎯 Use Cases

### NFT Marketplace
```python
# Mint NFTs for your marketplace
nft_ids = client.mint_nft_collection("marketplace_nfts.yaml")

# Handle sales and transfers
tx_id = client.send_tokens(nft_id, buyer_address, 1)
```

### Token Distribution
```python
# Distribute governance tokens
tx_ids = client.distribute_tokens(
    token_id="governance_token",
    config_file="governance_distribution.yaml"
)
```

### Gaming Tokens
```python
# Create in-game currency
currency_id = client.create_token(
    name="Game Gold",
    description="In-game currency",
    supply=1000000,
    decimals=0
)

# Reward players
tx_ids = client.airdrop_tokens(currency_id, player_addresses, rewards)
```

## 💡 Tips for Success

1. **Start with Testnet**: Always test your applications on testnet first
2. **Use Config Files**: Leverage YAML configs for complex operations
3. **Monitor Transactions**: Always wait for confirmations
4. **Handle Errors**: Implement proper error handling in your applications
5. **Keep Learning**: Explore the tutorials and examples regularly

---

**Ready to build amazing things with Ergo? Start coding! 🚀**