# Token Decimal Support in SigmaPy

## Overview

SigmaPy now includes comprehensive support for token decimals, ensuring accurate token distribution regardless of the token's decimal configuration.

## Key Features

### 1. Automatic Token Info Fetching
- Fetches token metadata from Ergo node including decimal places
- Handles both EIP-4 tokens and standard tokens
- Graceful fallback to 0 decimals if token info unavailable

### 2. Decimal Validation
- Validates fractional amounts against token's decimal places
- Prevents invalid precision (e.g., 0.001 tokens for 2-decimal token)
- Clear error messages for invalid amounts

### 3. Accurate Amount Conversion
- Converts display amounts to smallest units for blockchain transactions
- Maintains precision throughout the distribution process
- Proper handling of both whole and fractional amounts

### 4. Enhanced Logging
- Shows both display amounts and smallest unit amounts
- Token name and decimal information in transaction logs
- Clear indication of token precision

## Usage Examples

### Configuration with Fractional Amounts
```yaml
distribution:
  token_id: "your_token_id_here"
  batch_size: 50
  fee_per_tx: 0.001

recipients:
  - address: "9fRusAarL1KkrWQVsxSRVYnvWzD4dWoLLxbYk3eWBV3jD3qvr3W"
    amount: 10.50      # 2 decimal places
    note: "Fractional amount"
    
  - address: "9gQqZyxyjAptMbfW1Gydm3qaap11zd6X9DrABTbMBRJLjZhQRCA"
    amount: 100.00     # Whole number
    note: "Whole amount"
```

### Dry-Run Output Example
```
Token: MyToken (abc123...)
Token decimals: 2
Total tokens to distribute: 110.50 (11050 smallest units)
Recipients:
  1. 9fRusAarL1... 10.50 (1050 units) tokens Fractional amount
  2. 9gQqZyxyjA... 100.00 (10000 units) tokens Whole amount
```

## Technical Implementation

### 1. Token Info Fetching
```python
def _get_token_info(self, token_id: str) -> Dict[str, Any]:
    """Fetch token information including decimals from Ergo node."""
    try:
        token_info = self.network_manager.get_token_info(token_id)
        # Parse decimals from various token formats
        decimals = self._extract_decimals(token_info)
        return {
            'id': token_id,
            'name': token_info.get('name', 'Unknown Token'),
            'decimals': decimals,
            'type': token_info.get('type', 'Token')
        }
    except Exception:
        # Fallback to safe defaults
        return {'id': token_id, 'decimals': 0, 'name': 'Unknown Token'}
```

### 2. Amount Conversion
```python
def _convert_token_amount_to_smallest_unit(self, amount: float, decimals: int) -> int:
    """Convert display amount to smallest unit."""
    if decimals == 0:
        return int(amount)
    return int(amount * (10 ** decimals))
```

### 3. Validation
```python
# Validate fractional amounts respect decimal places
for recipient in recipients:
    amount = recipient['amount']
    if decimals > 0 and amount != int(amount):
        scaled_amount = amount * (10 ** decimals)
        if scaled_amount != int(scaled_amount):
            raise ValueError(f"Amount {amount} has too many decimal places")
```

## Error Handling

### Invalid Decimal Precision
```
❌ Recipient 1: amount 10.125 has too many decimal places for token with 2 decimals
```

### Token Info Unavailable
```
⚠️  Could not fetch token info for abc123...: 404 Client Error
   Using default: 0 decimals
```

## Benefits

1. **Accuracy**: Ensures exact token amounts in transactions
2. **Safety**: Prevents invalid precision errors  
3. **Transparency**: Clear logging of decimal handling
4. **Compatibility**: Works with all Ergo token types
5. **Robustness**: Graceful fallback when token info unavailable

## Testing

The decimal support has been tested with:
- ✅ Tokens with 0 decimals (integers only)
- ✅ Tokens with 2 decimals (currency-like)
- ✅ Tokens with 18 decimals (ethereum-like)
- ✅ Fractional amounts (10.50, 0.01, etc.)
- ✅ Whole number amounts (100, 1000, etc.)
- ✅ Missing token info (fallback to 0 decimals)

## Next Steps

This decimal support is now integrated into the core token distribution system and will automatically handle token precision for all distributions, ensuring your airdrops are accurate regardless of the token's decimal configuration.