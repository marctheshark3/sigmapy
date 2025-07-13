# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

SigmaPy is a comprehensive learning resource and Python library for Ergo blockchain development. It provides beginner-friendly tutorials, practical examples, and high-level APIs that abstract the complexity of ergo-lib-python bindings.

## Project Structure

### Core Architecture

```
src/sigmapy/
├── client/           # Main client interfaces
│   ├── ergo_client.py     # High-level ErgoClient API
│   ├── wallet_manager.py  # Wallet operations
│   └── network_manager.py # Network connectivity
├── operations/       # Specialized operation managers
│   ├── nft_minter.py      # NFT creation and minting
│   ├── token_manager.py   # Token operations
│   ├── contract_manager.py # Smart contract interactions
│   └── batch_processor.py # Batch operations
├── config/          # Configuration management
│   ├── config_parser.py   # YAML config parsing
│   ├── templates.py       # Config templates
│   └── validators.py      # Configuration validation
├── utils/           # Utility functions
│   ├── amount_utils.py    # ERG/nanoERG conversions
│   ├── env_utils.py       # Environment management
│   └── serialization_utils.py # Data serialization
├── tutorials/       # Step-by-step learning modules
│   └── basic_wallet.py    # Wallet operations tutorial
└── examples/        # Practical code examples
    ├── simple_payment.py   # Basic payment transactions
    └── advanced_transaction.py # Complex transaction building
```

### Configuration Files

- **`.env`** - Environment variables for wallet seed, network, API keys
- **`examples/configs/nft_collection.yaml`** - NFT collection configuration template
- **`examples/configs/token_distribution.yaml`** - Token distribution configuration template

## Development Commands

### Installation and Setup

```bash
# Install in development mode
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"

# Install with full blockchain support
pip install -e ".[full]"
```

### Testing

```bash
# Run all tests
pytest tests/

# Run installation verification
python examples/test_installation.py

# Run beginner demo (no blockchain required)
python examples/beginner_friendly_demo.py

# Test with real blockchain (requires .env setup)
python examples/run_advanced_transaction.py
```

### Code Quality

```bash
# Format code
black src/

# Lint code
flake8 src/

# Type checking
mypy src/

# Install pre-commit hooks
pre-commit install
```

### Documentation

```bash
# Install documentation dependencies
pip install -e ".[docs]"

# Build documentation
cd docs/
make html
```

## Architecture Patterns

### High-Level API Design

The `ErgoClient` class serves as the main entry point, providing simple one-line methods for complex operations:

```python
# Initialize client
client = ErgoClient()  # Uses .env file

# Common operations
nft_id = client.mint_nft(name="Art", description="Digital art")
token_id = client.create_token(name="MyToken", supply=1000000)
tx_ids = client.distribute_tokens(token_id, "config.yaml")
```

### Configuration-Driven Operations

SigmaPy emphasizes configuration files for batch operations:
- YAML files define NFT collections, token distributions
- Environment variables manage sensitive data (seed phrases, API keys)
- Templates provide starting points for common operations

### Modular Operation Managers

Specialized managers handle different operation types:
- `NFTMinter` - NFT creation and collection minting
- `TokenManager` - Token creation, distribution, airdrops
- `BatchProcessor` - Bulk operations with transaction batching
- `ContractManager` - Smart contract deployment and interaction

### Environment Management

The `EnvManager` utility loads configuration from:
1. `.env` files (primary)
2. Environment variables
3. Method parameters (fallback)

This pattern keeps sensitive data secure while providing flexible configuration options.

## Dependencies and Integration

### Core Dependencies

- **ergo-lib-python** - Official Ergo blockchain bindings (optional dependency)
- **requests** - HTTP client for node communication
- **PyYAML** - Configuration file parsing
- **python-dotenv** - Environment variable management

### Blockchain Integration

- Connects to Ergo nodes via REST API (local or public nodes)
- Supports both mainnet and testnet
- Handles wallet operations through ergo-lib-python bindings
- Implements transaction building, signing, and broadcasting

### Network Patterns

```python
# Demo mode (no real blockchain)
client = ErgoClient(demo_mode=True)

# Testnet for development
client = ErgoClient(network="testnet")

# Custom node with API key
client = ErgoClient(
    node_url="https://custom-node.com",
    api_key="your-key"
)
```

## Security Considerations

### Environment Variables

Always use `.env` files for sensitive data:

```bash
SIGMAPY_SEED_PHRASE="twelve word mnemonic phrase"
SIGMAPY_NETWORK="testnet"
SIGMAPY_DEMO_MODE="false"
```

### Demo Mode

The library includes a demo mode for testing without real blockchain operations:
- Set `SIGMAPY_DEMO_MODE="true"` in `.env`
- Or pass `demo_mode=True` to ErgoClient
- Simulates operations without actual transactions

### Validation

- All addresses are validated before use
- Configuration files are validated against schemas
- Transaction parameters are checked before signing

## Common Workflows

### NFT Collection Creation

1. Create `nft_collection.yaml` with collection metadata
2. Use `client.mint_nft_collection("config.yaml")`
3. Monitor transaction status until confirmation

### Token Distribution

1. Create `token_distribution.yaml` with recipient addresses
2. Use `client.distribute_tokens(token_id, "config.yaml")`
3. Operations are automatically batched for efficiency

### Wallet Operations

1. Initialize client with seed phrase in `.env`
2. Check balance: `client.get_balance()`
3. Get addresses: `client.get_addresses(count=5)`
4. Send payments: `client.send_erg(recipient, amount)`

## Error Handling Patterns

The library implements comprehensive error handling:
- Network timeouts with retry logic
- Invalid address format validation
- Insufficient balance checks
- Configuration file validation errors

Most operations return detailed error messages with suggested resolutions.

## Testing Strategy

### Unit Tests
- Mock ergo-lib-python for isolated testing
- Test configuration parsing and validation
- Verify utility functions and conversions

### Integration Tests
- Use demo mode for blockchain operation testing
- Test against testnet for full integration
- Validate configuration file processing

### Example Scripts
- `test_installation.py` - Verifies setup
- `beginner_friendly_demo.py` - Demonstrates core features
- `secure_setup_demo.py` - Shows security best practices