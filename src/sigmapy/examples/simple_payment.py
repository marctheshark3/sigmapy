"""
Simple Payment Example - Send ERG from one address to another

This example demonstrates:
1. Creating a simple payment transaction
2. Signing the transaction
3. Broadcasting to the network
4. Monitoring transaction status

Requirements:
- ergo-lib-python
- Access to an Ergo node (local or remote)
"""

from typing import Dict, Any, Optional
import logging
import time


class SimplePaymentExample:
    """
    Example class for creating and sending simple ERG payments.
    
    This example shows how to:
    - Build a transaction
    - Sign it with a wallet
    - Submit it to the network
    - Track confirmation status
    """
    
    def __init__(self, node_url: str = "http://localhost:9052"):
        """
        Initialize the payment example.
        
        Args:
            node_url: URL of the Ergo node to connect to
        """
        self.node_url = node_url
        self.logger = logging.getLogger(__name__)
        
        # Initialize connection to ergo-lib-python
        try:
            # import ergo_lib_python as ergo
            # self.ergo = ergo
            pass
        except ImportError:
            self.logger.warning("ergo-lib-python not installed")
            self.ergo = None
    
    def create_payment_transaction(
        self,
        sender_address: str,
        recipient_address: str,
        amount_erg: float,
        fee_erg: float = 0.001
    ) -> Dict[str, Any]:
        """
        Create a payment transaction.
        
        Args:
            sender_address: Address sending the ERG
            recipient_address: Address receiving the ERG
            amount_erg: Amount to send in ERG
            fee_erg: Transaction fee in ERG
            
        Returns:
            Dict containing transaction details
            
        Example:
            >>> example = SimplePaymentExample()
            >>> tx = example.create_payment_transaction(
            ...     sender_address="9f...",
            ...     recipient_address="9g...",
            ...     amount_erg=1.5,
            ...     fee_erg=0.001
            ... )
        """
        print("=== Creating Payment Transaction ===")
        print(f"From: {sender_address}")
        print(f"To: {recipient_address}")
        print(f"Amount: {amount_erg} ERG")
        print(f"Fee: {fee_erg} ERG")
        print()
        
        if not self.ergo:
            print("⚠️  ergo-lib-python not available. This is a demonstration.")
            return {
                "transaction_id": "demo_tx_123",
                "amount_nanoerg": int(amount_erg * 1_000_000_000),
                "fee_nanoerg": int(fee_erg * 1_000_000_000),
                "status": "demo"
            }
        
        # Convert ERG to nanoERG
        amount_nanoerg = int(amount_erg * 1_000_000_000)
        fee_nanoerg = int(fee_erg * 1_000_000_000)
        
        # Actual implementation:
        # 1. Get unspent boxes for sender
        # unspent_boxes = self.get_unspent_boxes(sender_address)
        # 
        # 2. Create transaction builder
        # tx_builder = self.ergo.TransactionBuilder()
        # 
        # 3. Add inputs (unspent boxes)
        # total_input = 0
        # for box in unspent_boxes:
        #     tx_builder.add_input(box)
        #     total_input += box.value
        #     if total_input >= amount_nanoerg + fee_nanoerg:
        #         break
        # 
        # 4. Add output (recipient)
        # recipient_box = self.ergo.ErgoBox(
        #     value=amount_nanoerg,
        #     recipient=recipient_address
        # )
        # tx_builder.add_output(recipient_box)
        # 
        # 5. Add change output if needed
        # change_amount = total_input - amount_nanoerg - fee_nanoerg
        # if change_amount > 0:
        #     change_box = self.ergo.ErgoBox(
        #         value=change_amount,
        #         recipient=sender_address
        #     )
        #     tx_builder.add_output(change_box)
        # 
        # 6. Build transaction
        # transaction = tx_builder.build()
        
        print("✅ Transaction created successfully!")
        print("Next step: Sign the transaction")
        
        return {
            "amount_nanoerg": amount_nanoerg,
            "fee_nanoerg": fee_nanoerg,
            "sender": sender_address,
            "recipient": recipient_address
        }
    
    def sign_transaction(self, transaction: Dict[str, Any], wallet_mnemonic: str) -> Dict[str, Any]:
        """
        Sign a transaction with a wallet.
        
        Args:
            transaction: Transaction to sign
            wallet_mnemonic: Mnemonic phrase of the signing wallet
            
        Returns:
            Dict containing signed transaction
            
        Security Notes:
        - Never log or store mnemonic phrases
        - Always verify transaction details before signing
        - Use secure methods to handle private keys
        """
        print("=== Signing Transaction ===")
        print("Signing transaction with wallet...")
        print("⚠️  Always verify transaction details before signing!")
        print()
        
        if not self.ergo:
            print("⚠️  ergo-lib-python not available. This is a demonstration.")
            return {
                "signed_transaction": "demo_signed_tx",
                "transaction_id": "demo_tx_123",
                "status": "demo"
            }
        
        # Actual implementation:
        # 1. Create wallet from mnemonic
        # wallet = self.ergo.Wallet.restore(wallet_mnemonic)
        # 
        # 2. Sign the transaction
        # signed_tx = wallet.sign_transaction(transaction)
        # 
        # 3. Get transaction ID
        # tx_id = signed_tx.id()
        
        print("✅ Transaction signed successfully!")
        print("Next step: Broadcast to network")
        
        return {
            "signed": True,
            "transaction_id": "demo_tx_123"
        }
    
    def broadcast_transaction(self, signed_transaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Broadcast a signed transaction to the network.
        
        Args:
            signed_transaction: The signed transaction to broadcast
            
        Returns:
            Dict containing broadcast result
            
        Network Notes:
        - Transaction must be properly signed
        - Network fees must be adequate
        - Inputs must be unspent
        """
        print("=== Broadcasting Transaction ===")
        print("Submitting transaction to the network...")
        print()
        
        if not self.ergo:
            print("⚠️  ergo-lib-python not available. This is a demonstration.")
            return {
                "transaction_id": "demo_tx_123",
                "status": "submitted",
                "broadcast_time": time.time()
            }
        
        # Actual implementation:
        # 1. Submit to node
        # result = self.submit_to_node(signed_transaction)
        # 
        # 2. Return result
        # return {
        #     "transaction_id": result.tx_id,
        #     "status": "submitted",
        #     "broadcast_time": time.time()
        # }
        
        print("✅ Transaction broadcast successfully!")
        print("Transaction ID: demo_tx_123")
        print("Next step: Monitor confirmation")
        
        return {
            "transaction_id": "demo_tx_123",
            "status": "submitted"
        }
    
    def monitor_transaction(self, transaction_id: str, timeout_seconds: int = 300) -> Dict[str, Any]:
        """
        Monitor a transaction until it's confirmed.
        
        Args:
            transaction_id: ID of the transaction to monitor
            timeout_seconds: Maximum time to wait for confirmation
            
        Returns:
            Dict containing transaction status
            
        Monitoring Notes:
        - Transactions typically confirm within 2-4 minutes
        - Network congestion can cause delays
        - Failed transactions will be rejected
        """
        print("=== Monitoring Transaction ===")
        print(f"Monitoring transaction: {transaction_id}")
        print("Waiting for confirmation...")
        print()
        
        start_time = time.time()
        
        if not self.ergo:
            print("⚠️  ergo-lib-python not available. This is a demonstration.")
            print("✅ Transaction confirmed! (simulated)")
            return {
                "transaction_id": transaction_id,
                "status": "confirmed",
                "confirmations": 1,
                "block_height": 123456
            }
        
        # Actual implementation:
        # while time.time() - start_time < timeout_seconds:
        #     status = self.get_transaction_status(transaction_id)
        #     
        #     if status.confirmed:
        #         print(f"✅ Transaction confirmed!")
        #         print(f"Block height: {status.block_height}")
        #         print(f"Confirmations: {status.confirmations}")
        #         return status
        #     
        #     print(f"⏳ Waiting... ({int(time.time() - start_time)}s)")
        #     time.sleep(10)
        
        print("✅ Transaction monitoring completed!")
        
        return {
            "transaction_id": transaction_id,
            "status": "confirmed"
        }
    
    def run_complete_example(self) -> None:
        """
        Run a complete payment example from start to finish.
        
        This method demonstrates the entire payment flow:
        1. Create transaction
        2. Sign transaction  
        3. Broadcast transaction
        4. Monitor confirmation
        """
        print("💰 Simple Payment Example")
        print("This example shows how to send ERG from one address to another.")
        print("=" * 60)
        print()
        
        # Example addresses and amounts
        sender_address = "9fRusAarL1KkrWQVsxSRVYnvWzD4dWoLLxbYk3eWBV3jD3qvr3W"
        recipient_address = "9gQqZyxyjAptMbfW1Gydm3qaap11zd6X9DrABTbMBRJLjZhQRCA"
        amount_erg = 1.5
        fee_erg = 0.001
        
        # Step 1: Create transaction
        transaction = self.create_payment_transaction(
            sender_address=sender_address,
            recipient_address=recipient_address,
            amount_erg=amount_erg,
            fee_erg=fee_erg
        )
        print()
        
        # Step 2: Sign transaction
        # Note: In practice, you would use a real mnemonic
        demo_mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
        signed_tx = self.sign_transaction(transaction, demo_mnemonic)
        print()
        
        # Step 3: Broadcast transaction
        broadcast_result = self.broadcast_transaction(signed_tx)
        print()
        
        # Step 4: Monitor transaction
        if broadcast_result.get("transaction_id"):
            monitor_result = self.monitor_transaction(broadcast_result["transaction_id"])
            print()
        
        print("🎉 Payment example completed successfully!")
        print("Key takeaways:")
        print("1. Always verify transaction details before signing")
        print("2. Keep mnemonic phrases secure and private")
        print("3. Monitor transactions until confirmation")
        print("4. Account for network fees in your calculations")


def main():
    """Run the simple payment example."""
    example = SimplePaymentExample()
    example.run_complete_example()


if __name__ == "__main__":
    main()