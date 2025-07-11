"""
Amount utility functions for ERG and nanoERG conversions

This module provides helper functions for working with Ergo amounts:
- Converting between ERG and nanoERG
- Formatting amounts for display
- Validating amount values
- Handling precision and rounding
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Union


class AmountUtils:
    """
    Utility class for handling Ergo amount conversions and formatting.
    
    Constants:
        NANOERG_PER_ERG: Number of nanoERG in 1 ERG (1,000,000,000)
        MIN_BOX_VALUE: Minimum value for an ErgoBox in nanoERG
    """
    
    NANOERG_PER_ERG = 1_000_000_000
    MIN_BOX_VALUE = 1_000_000  # 0.001 ERG minimum
    
    @staticmethod
    def erg_to_nanoerg(erg_amount: Union[float, str, Decimal]) -> int:
        """
        Convert ERG amount to nanoERG.
        
        Args:
            erg_amount: Amount in ERG (supports float, string, or Decimal)
            
        Returns:
            Amount in nanoERG as integer
            
        Raises:
            ValueError: If amount is negative or invalid
            
        Examples:
            >>> AmountUtils.erg_to_nanoerg(1.5)
            1500000000
            >>> AmountUtils.erg_to_nanoerg("0.001")
            1000000
        """
        try:
            # Convert to Decimal for precise arithmetic
            if isinstance(erg_amount, (int, float)):
                decimal_amount = Decimal(str(erg_amount))
            else:
                decimal_amount = Decimal(erg_amount)
            
            if decimal_amount < 0:
                raise ValueError("Amount cannot be negative")
            
            # Multiply by nanoERG per ERG and round to nearest integer
            nanoerg_amount = decimal_amount * AmountUtils.NANOERG_PER_ERG
            return int(nanoerg_amount.quantize(Decimal('1'), rounding=ROUND_HALF_UP))
            
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid ERG amount: {erg_amount}") from e
    
    @staticmethod
    def nanoerg_to_erg(nanoerg_amount: int) -> Decimal:
        """
        Convert nanoERG amount to ERG.
        
        Args:
            nanoerg_amount: Amount in nanoERG
            
        Returns:
            Amount in ERG as Decimal
            
        Raises:
            ValueError: If amount is negative
            
        Examples:
            >>> AmountUtils.nanoerg_to_erg(1500000000)
            Decimal('1.5')
            >>> AmountUtils.nanoerg_to_erg(1000000)
            Decimal('0.001')
        """
        if nanoerg_amount < 0:
            raise ValueError("Amount cannot be negative")
        
        return Decimal(nanoerg_amount) / AmountUtils.NANOERG_PER_ERG
    
    @staticmethod
    def format_erg_amount(amount: Union[int, float, Decimal], decimals: int = 9) -> str:
        """
        Format an ERG amount for display.
        
        Args:
            amount: Amount in ERG
            decimals: Number of decimal places to show
            
        Returns:
            Formatted string representation
            
        Examples:
            >>> AmountUtils.format_erg_amount(1.5)
            '1.500000000'
            >>> AmountUtils.format_erg_amount(1.5, decimals=3)
            '1.500'
        """
        if isinstance(amount, (int, float)):
            decimal_amount = Decimal(str(amount))
        else:
            decimal_amount = Decimal(amount)
        
        # Format with specified decimal places
        format_str = f"{{:.{decimals}f}}"
        return format_str.format(decimal_amount)
    
    @staticmethod
    def format_nanoerg_amount(nanoerg_amount: int) -> str:
        """
        Format a nanoERG amount as ERG for display.
        
        Args:
            nanoerg_amount: Amount in nanoERG
            
        Returns:
            Formatted string representation in ERG
            
        Examples:
            >>> AmountUtils.format_nanoerg_amount(1500000000)
            '1.500000000 ERG'
            >>> AmountUtils.format_nanoerg_amount(1000000)
            '0.001000000 ERG'
        """
        erg_amount = AmountUtils.nanoerg_to_erg(nanoerg_amount)
        return f"{AmountUtils.format_erg_amount(erg_amount)} ERG"
    
    @staticmethod
    def validate_amount(amount: Union[int, float, str, Decimal], min_value: float = 0) -> bool:
        """
        Validate an amount value.
        
        Args:
            amount: Amount to validate
            min_value: Minimum allowed value
            
        Returns:
            True if amount is valid, False otherwise
            
        Examples:
            >>> AmountUtils.validate_amount(1.5)
            True
            >>> AmountUtils.validate_amount(-1)
            False
            >>> AmountUtils.validate_amount("abc")
            False
        """
        try:
            if isinstance(amount, (int, float)):
                decimal_amount = Decimal(str(amount))
            else:
                decimal_amount = Decimal(amount)
            
            return decimal_amount >= min_value
            
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_box_value(nanoerg_amount: int) -> bool:
        """
        Validate that an amount meets minimum box value requirements.
        
        Args:
            nanoerg_amount: Amount in nanoERG
            
        Returns:
            True if amount meets minimum requirements
            
        Examples:
            >>> AmountUtils.validate_box_value(1000000)
            True
            >>> AmountUtils.validate_box_value(500000)
            False
        """
        return nanoerg_amount >= AmountUtils.MIN_BOX_VALUE
    
    @staticmethod
    def calculate_change(
        total_input: int,
        amount_to_send: int,
        fee: int
    ) -> int:
        """
        Calculate change amount for a transaction.
        
        Args:
            total_input: Total input amount in nanoERG
            amount_to_send: Amount to send in nanoERG
            fee: Transaction fee in nanoERG
            
        Returns:
            Change amount in nanoERG
            
        Raises:
            ValueError: If inputs are insufficient
            
        Examples:
            >>> AmountUtils.calculate_change(2000000000, 1000000000, 1000000)
            999000000
        """
        if total_input < amount_to_send + fee:
            raise ValueError("Insufficient funds for transaction")
        
        change = total_input - amount_to_send - fee
        
        # Ensure change meets minimum box value if it's not zero
        if change > 0 and change < AmountUtils.MIN_BOX_VALUE:
            raise ValueError(f"Change amount {change} is below minimum box value {AmountUtils.MIN_BOX_VALUE}")
        
        return change
    
    @staticmethod
    def suggest_fee(transaction_size_bytes: int = 1000) -> int:
        """
        Suggest a transaction fee based on transaction size.
        
        Args:
            transaction_size_bytes: Estimated transaction size in bytes
            
        Returns:
            Suggested fee in nanoERG
            
        Examples:
            >>> AmountUtils.suggest_fee(1000)
            1000000
            >>> AmountUtils.suggest_fee(2000)
            2000000
        """
        # Simple fee calculation: 1000 nanoERG per byte
        # This is a basic example - real fee calculation would be more sophisticated
        base_fee = 1000000  # 0.001 ERG minimum
        size_fee = transaction_size_bytes * 1000  # 1000 nanoERG per byte
        
        return max(base_fee, size_fee)


def main():
    """Demonstrate amount utility functions."""
    print("💰 Amount Utilities Demo")
    print("=" * 40)
    
    # Conversion examples
    print("\n1. ERG to nanoERG conversions:")
    amounts = [1.0, 1.5, 0.001, 10.123456789]
    for erg in amounts:
        nanoerg = AmountUtils.erg_to_nanoerg(erg)
        print(f"   {erg} ERG = {nanoerg:,} nanoERG")
    
    print("\n2. nanoERG to ERG conversions:")
    nanoerg_amounts = [1000000000, 1500000000, 1000000, 10123456789]
    for nanoerg in nanoerg_amounts:
        erg = AmountUtils.nanoerg_to_erg(nanoerg)
        print(f"   {nanoerg:,} nanoERG = {erg} ERG")
    
    print("\n3. Formatting examples:")
    print(f"   1.5 ERG formatted: {AmountUtils.format_erg_amount(1.5)}")
    print(f"   1.5 ERG (3 decimals): {AmountUtils.format_erg_amount(1.5, decimals=3)}")
    print(f"   1500000000 nanoERG: {AmountUtils.format_nanoerg_amount(1500000000)}")
    
    print("\n4. Validation examples:")
    test_amounts = [1.5, -1, "abc", 0.001]
    for amount in test_amounts:
        valid = AmountUtils.validate_amount(amount)
        print(f"   {amount} is valid: {valid}")
    
    print("\n5. Change calculation:")
    try:
        change = AmountUtils.calculate_change(2000000000, 1000000000, 1000000)
        print(f"   Change: {AmountUtils.format_nanoerg_amount(change)}")
    except ValueError as e:
        print(f"   Error: {e}")
    
    print("\n6. Fee suggestion:")
    fee = AmountUtils.suggest_fee(1000)
    print(f"   Suggested fee: {AmountUtils.format_nanoerg_amount(fee)}")


if __name__ == "__main__":
    main()