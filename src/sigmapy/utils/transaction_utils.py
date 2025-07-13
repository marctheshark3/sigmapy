"""
Transaction utilities for Ergo blockchain operations.

This module provides utility functions for transaction building,
validation, and processing.
"""

from typing import Dict, List, Optional, Any
import time
import hashlib

try:
    import ergo_lib_python as ergo
    ERGO_LIB_AVAILABLE = True
except ImportError:
    ERGO_LIB_AVAILABLE = False
    ergo = None


class TransactionUtils:
    """Utilities for Ergo transaction operations."""
    
    # Minimum ERG per output box
    MIN_BOX_VALUE_NANOERG = 1_000_000  # 0.001 ERG
    
    @staticmethod
    def calculate_min_fee(num_inputs: int, num_outputs: int) -> int:
        """
        Calculate minimum transaction fee.
        
        Args:
            num_inputs: Number of transaction inputs
            num_outputs: Number of transaction outputs
            
        Returns:
            Minimum fee in nanoERG
        """
        # Basic fee calculation (can be refined)
        base_fee = 1_000_000  # 0.001 ERG base
        input_fee = num_inputs * 500_000  # 0.0005 ERG per input
        output_fee = num_outputs * 200_000  # 0.0002 ERG per output
        
        return base_fee + input_fee + output_fee
    
    @staticmethod
    def calculate_total_erg_needed(
        recipients: List[Dict],
        fee_nanoerg: int
    ) -> int:
        """
        Calculate total ERG needed for a transaction.
        
        Args:
            recipients: List of recipient dictionaries
            fee_nanoerg: Transaction fee in nanoERG
            
        Returns:
            Total nanoERG needed
        """
        min_box_values = len(recipients) * TransactionUtils.MIN_BOX_VALUE_NANOERG
        return min_box_values + fee_nanoerg
    
    @staticmethod
    def validate_transaction_data(tx_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate transaction data structure.
        
        Args:
            tx_data: Transaction data dictionary
            
        Returns:
            Validation result
        """
        errors = []
        warnings = []
        
        # Check required fields
        required_fields = ['inputs', 'outputs']
        for field in required_fields:
            if field not in tx_data:
                errors.append(f"Missing required field: {field}")
        
        # Validate inputs
        inputs = tx_data.get('inputs', [])
        if not inputs:
            errors.append("Transaction must have at least one input")
        
        # Validate outputs
        outputs = tx_data.get('outputs', [])
        if not outputs:
            errors.append("Transaction must have at least one output")
        
        # Check box values
        for i, output in enumerate(outputs):
            value = output.get('value', 0)
            if value < TransactionUtils.MIN_BOX_VALUE_NANOERG:
                errors.append(
                    f"Output {i+1} value {value} below minimum "
                    f"{TransactionUtils.MIN_BOX_VALUE_NANOERG}"
                )
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    @staticmethod
    def estimate_transaction_size(
        num_inputs: int,
        num_outputs: int,
        has_tokens: bool = False
    ) -> int:
        """
        Estimate transaction size in bytes.
        
        Args:
            num_inputs: Number of inputs
            num_outputs: Number of outputs
            has_tokens: Whether transaction includes tokens
            
        Returns:
            Estimated size in bytes
        """
        # Rough estimation
        base_size = 100  # Basic transaction overhead
        input_size = num_inputs * 150  # Per input
        output_size = num_outputs * 50  # Per output
        token_overhead = 50 if has_tokens else 0
        
        return base_size + input_size + output_size + token_overhead
    
    @staticmethod
    def create_transaction_id(tx_data: Dict[str, Any]) -> str:
        """
        Create a transaction ID (for demo purposes).
        
        Args:
            tx_data: Transaction data
            
        Returns:
            Transaction ID string
        """
        # Create a hash-based ID for demo mode
        timestamp = str(int(time.time()))
        content = str(tx_data)
        hash_input = f"{timestamp}{content}".encode()
        
        tx_hash = hashlib.sha256(hash_input).hexdigest()
        return f"demo_tx_{tx_hash[:16]}"
    
    @staticmethod
    def format_transaction_summary(tx_data: Dict[str, Any]) -> str:
        """
        Format transaction data for display.
        
        Args:
            tx_data: Transaction data
            
        Returns:
            Formatted summary string
        """
        inputs = tx_data.get('inputs', [])
        outputs = tx_data.get('outputs', [])
        fee = tx_data.get('fee_nanoerg', 0)
        
        summary = f"Transaction Summary:\n"
        summary += f"  Inputs: {len(inputs)}\n"
        summary += f"  Outputs: {len(outputs)}\n"
        summary += f"  Fee: {fee / 1_000_000:.6f} ERG\n"
        
        if outputs:
            total_output_value = sum(o.get('value', 0) for o in outputs)
            summary += f"  Total Output Value: {total_output_value / 1_000_000:.6f} ERG\n"
        
        return summary
    
    @staticmethod
    def split_into_batches(
        items: List[Any],
        batch_size: int
    ) -> List[List[Any]]:
        """
        Split items into batches.
        
        Args:
            items: List of items to batch
            batch_size: Size of each batch
            
        Returns:
            List of batches
        """
        batches = []
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batches.append(batch)
        return batches
    
    @staticmethod
    def calculate_batch_summary(
        recipients: List[Dict],
        batch_size: int,
        fee_per_tx: float
    ) -> Dict[str, Any]:
        """
        Calculate summary for batched operations.
        
        Args:
            recipients: List of recipients
            batch_size: Batch size
            fee_per_tx: Fee per transaction in ERG
            
        Returns:
            Batch summary
        """
        import math
        
        total_recipients = len(recipients)
        total_tokens = sum(r.get('amount', 0) for r in recipients)
        num_batches = math.ceil(total_recipients / batch_size)
        
        min_erg_per_recipient = TransactionUtils.MIN_BOX_VALUE_NANOERG / 1_000_000
        total_min_erg = total_recipients * min_erg_per_recipient
        total_fees = num_batches * fee_per_tx
        total_erg_needed = total_min_erg + total_fees
        
        return {
            'total_recipients': total_recipients,
            'total_tokens': total_tokens,
            'num_batches': num_batches,
            'batch_size': batch_size,
            'min_erg_per_recipient': min_erg_per_recipient,
            'total_min_erg': total_min_erg,
            'total_fees': total_fees,
            'total_erg_needed': total_erg_needed
        }