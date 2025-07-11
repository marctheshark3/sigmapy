"""
Advanced Transaction Example - Multiple Outputs with Registers and Extensions

This example demonstrates:
1. Building a transaction with multiple outputs
2. Adding data to registers (R4-R9)
3. Using context extensions for additional data
4. Serializing complex data structures
5. Signing and submitting the transaction

This is an advanced example showing how to:
- Store custom data in ErgoBoxes
- Use serializers for complex data types
- Handle multiple outputs with different purposes
- Work with context extensions for transaction metadata

Requirements:
- ergo-lib-python
- Access to an Ergo node (local or remote)
"""

from typing import Dict, Any, List, Optional, Union
import json
import base64
import logging
from dataclasses import dataclass


@dataclass
class RegisterData:
    """Data structure for ErgoBox register content."""
    register_id: str  # R4, R5, R6, R7, R8, R9
    data_type: str   # "Int", "Long", "String", "Bytes", "GroupElement"
    value: Any
    serialized: Optional[str] = None


@dataclass
class OutputSpec:
    """Specification for a transaction output."""
    recipient_address: str
    amount_nanoerg: int
    registers: List[RegisterData]
    tokens: List[Dict[str, Any]] = None


class AdvancedTransactionExample:
    """
    Advanced transaction example with registers and extensions.
    
    This class demonstrates complex transaction building including:
    - Multiple outputs with custom data
    - Register serialization and deserialization
    - Context extensions for metadata
    - Complete transaction lifecycle
    """
    
    def __init__(self, node_url: str = "http://localhost:9052"):
        """
        Initialize the advanced transaction example.
        
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
    
    def serialize_register_data(self, register_data: RegisterData) -> str:
        """
        Serialize data for storage in ErgoBox registers.
        
        Args:
            register_data: Data to serialize
            
        Returns:
            Serialized data as hex string
            
        Register Types:
        - R4-R9: Available for custom data
        - Each register can store different Sigma types
        - Data must be properly serialized according to Sigma protocol
        """
        print(f"=== Serializing Register {register_data.register_id} ===")
        print(f"Type: {register_data.data_type}")
        print(f"Value: {register_data.value}")
        
        if not self.ergo:
            print("⚠️  ergo-lib-python not available. This is a demonstration.")
            
            # Simulated serialization for different data types
            if register_data.data_type == "Int":
                serialized = f"0400{register_data.value:08x}"
            elif register_data.data_type == "Long":
                serialized = f"0500{register_data.value:016x}"
            elif register_data.data_type == "String":
                text_bytes = register_data.value.encode('utf-8')
                length = len(text_bytes)
                serialized = f"0e{length:02x}{text_bytes.hex()}"
            elif register_data.data_type == "Bytes":
                if isinstance(register_data.value, str):
                    # Assume hex string
                    serialized = f"0e{len(register_data.value)//2:02x}{register_data.value}"
                else:
                    # Assume bytes
                    serialized = f"0e{len(register_data.value):02x}{register_data.value.hex()}"
            else:
                serialized = "0400deadbeef"  # Placeholder
            
            register_data.serialized = serialized
            print(f"Serialized: {serialized}")
            return serialized
        
        # Actual implementation with ergo-lib-python:
        # serializer = self.ergo.ConstantSerializer()
        # 
        # if register_data.data_type == "Int":
        #     constant = self.ergo.Constant.from_int(register_data.value)
        # elif register_data.data_type == "Long":
        #     constant = self.ergo.Constant.from_long(register_data.value)
        # elif register_data.data_type == "String":
        #     string_bytes = register_data.value.encode('utf-8')
        #     constant = self.ergo.Constant.from_byte_array(string_bytes)
        # elif register_data.data_type == "Bytes":
        #     if isinstance(register_data.value, str):
        #         bytes_data = bytes.fromhex(register_data.value)
        #     else:
        #         bytes_data = register_data.value
        #     constant = self.ergo.Constant.from_byte_array(bytes_data)
        # elif register_data.data_type == "GroupElement":
        #     constant = self.ergo.Constant.from_group_element(register_data.value)
        # else:
        #     raise ValueError(f"Unsupported data type: {register_data.data_type}")
        # 
        # serialized = serializer.serialize(constant)
        # register_data.serialized = serialized
        # return serialized
        
        print("✅ Register data serialized successfully!")
        return register_data.serialized
    
    def create_context_extensions(self, metadata: Dict[str, Any]) -> Dict[str, str]:
        """
        Create context extensions for transaction metadata.
        
        Args:
            metadata: Dictionary of metadata to include
            
        Returns:
            Dictionary of serialized context extensions
            
        Context Extensions:
        - Additional data attached to transaction
        - Not stored in boxes, but available during execution
        - Useful for providing context to smart contracts
        """
        print("=== Creating Context Extensions ===")
        print(f"Metadata: {json.dumps(metadata, indent=2)}")
        
        extensions = {}
        
        if not self.ergo:
            print("⚠️  ergo-lib-python not available. This is a demonstration.")
            
            # Simulated context extension serialization
            for key, value in metadata.items():
                if isinstance(value, str):
                    # Serialize string
                    value_bytes = value.encode('utf-8')
                    extensions[key] = f"0e{len(value_bytes):02x}{value_bytes.hex()}"
                elif isinstance(value, int):
                    # Serialize integer
                    extensions[key] = f"0400{value:08x}"
                elif isinstance(value, dict) or isinstance(value, list):
                    # Serialize JSON as string
                    json_str = json.dumps(value)
                    json_bytes = json_str.encode('utf-8')
                    extensions[key] = f"0e{len(json_bytes):02x}{json_bytes.hex()}"
                else:
                    # Default to string representation
                    str_repr = str(value)
                    str_bytes = str_repr.encode('utf-8')
                    extensions[key] = f"0e{len(str_bytes):02x}{str_bytes.hex()}"
            
            print("Context extensions created (simulated):")
            for key, value in extensions.items():
                print(f"  {key}: {value}")
            
            return extensions
        
        # Actual implementation:
        # serializer = self.ergo.ConstantSerializer()
        # 
        # for key, value in metadata.items():
        #     if isinstance(value, str):
        #         constant = self.ergo.Constant.from_byte_array(value.encode('utf-8'))
        #     elif isinstance(value, int):
        #         constant = self.ergo.Constant.from_int(value)
        #     elif isinstance(value, dict) or isinstance(value, list):
        #         json_str = json.dumps(value)
        #         constant = self.ergo.Constant.from_byte_array(json_str.encode('utf-8'))
        #     else:
        #         str_repr = str(value)
        #         constant = self.ergo.Constant.from_byte_array(str_repr.encode('utf-8'))
        #     
        #     extensions[key] = serializer.serialize(constant)
        
        print("✅ Context extensions created successfully!")
        return extensions
    
    def build_advanced_transaction(
        self,
        sender_address: str,
        outputs: List[OutputSpec],
        context_extensions: Dict[str, str],
        fee_nanoerg: int = 1000000
    ) -> Dict[str, Any]:
        """
        Build an advanced transaction with multiple outputs and custom data.
        
        Args:
            sender_address: Address sending the transaction
            outputs: List of output specifications
            context_extensions: Context extensions for the transaction
            fee_nanoerg: Transaction fee in nanoERG
            
        Returns:
            Dictionary containing transaction details
            
        Transaction Structure:
        - Multiple outputs with different purposes
        - Custom data in registers
        - Context extensions for metadata
        - Proper fee calculation
        """
        print("=== Building Advanced Transaction ===")
        print(f"Sender: {sender_address}")
        print(f"Number of outputs: {len(outputs)}")
        print(f"Fee: {fee_nanoerg} nanoERG")
        print()
        
        # Calculate total amount needed
        total_amount = sum(output.amount_nanoerg for output in outputs) + fee_nanoerg
        print(f"Total amount needed: {total_amount} nanoERG")
        
        if not self.ergo:
            print("⚠️  ergo-lib-python not available. This is a demonstration.")
            
            # Simulate transaction building
            transaction_data = {
                "inputs": [
                    {
                        "box_id": "demo_input_box_123",
                        "value": total_amount + 1000000,  # Extra for change
                        "address": sender_address
                    }
                ],
                "outputs": [],
                "context_extensions": context_extensions,
                "fee": fee_nanoerg
            }
            
            # Process each output
            for i, output in enumerate(outputs):
                print(f"\nProcessing output {i+1}:")
                print(f"  Recipient: {output.recipient_address}")
                print(f"  Amount: {output.amount_nanoerg} nanoERG")
                
                # Serialize registers
                serialized_registers = {}
                for register_data in output.registers:
                    serialized = self.serialize_register_data(register_data)
                    serialized_registers[register_data.register_id] = serialized
                
                output_data = {
                    "recipient": output.recipient_address,
                    "value": output.amount_nanoerg,
                    "registers": serialized_registers,
                    "tokens": output.tokens or []
                }
                
                transaction_data["outputs"].append(output_data)
            
            # Add change output if needed
            input_total = transaction_data["inputs"][0]["value"]
            change_amount = input_total - total_amount
            if change_amount > 1000000:  # Min box value
                change_output = {
                    "recipient": sender_address,
                    "value": change_amount,
                    "registers": {},
                    "tokens": []
                }
                transaction_data["outputs"].append(change_output)
                print(f"\nAdded change output: {change_amount} nanoERG")
            
            print("\n✅ Transaction built successfully!")
            return transaction_data
        
        # Actual implementation:
        # 1. Get unspent boxes for sender
        # unspent_boxes = self.get_unspent_boxes(sender_address)
        # 
        # 2. Create transaction builder
        # tx_builder = self.ergo.TransactionBuilder()
        # 
        # 3. Add inputs
        # total_input = 0
        # for box in unspent_boxes:
        #     tx_builder.add_input(box)
        #     total_input += box.value
        #     if total_input >= total_amount:
        #         break
        # 
        # 4. Add outputs with registers
        # for output in outputs:
        #     # Create output box
        #     output_builder = self.ergo.ErgoBoxBuilder(
        #         value=output.amount_nanoerg,
        #         recipient=output.recipient_address
        #     )
        #     
        #     # Add registers
        #     for register_data in output.registers:
        #         register_bytes = bytes.fromhex(register_data.serialized)
        #         output_builder.set_register(register_data.register_id, register_bytes)
        #     
        #     # Add tokens if present
        #     if output.tokens:
        #         for token in output.tokens:
        #             output_builder.add_token(token["id"], token["amount"])
        #     
        #     box = output_builder.build()
        #     tx_builder.add_output(box)
        # 
        # 5. Add change output if needed
        # change_amount = total_input - total_amount
        # if change_amount > self.ergo.MIN_BOX_VALUE:
        #     change_box = self.ergo.ErgoBox(
        #         value=change_amount,
        #         recipient=sender_address
        #     )
        #     tx_builder.add_output(change_box)
        # 
        # 6. Set context extensions
        # for key, value in context_extensions.items():
        #     tx_builder.set_context_extension(key, bytes.fromhex(value))
        # 
        # 7. Build transaction
        # transaction = tx_builder.build()
        
        print("✅ Advanced transaction built successfully!")
        return {}
    
    def sign_advanced_transaction(
        self,
        transaction: Dict[str, Any],
        wallet_mnemonic: str,
        context_extensions: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Sign an advanced transaction with context extensions.
        
        Args:
            transaction: Transaction to sign
            wallet_mnemonic: Mnemonic phrase of the signing wallet
            context_extensions: Context extensions for signing
            
        Returns:
            Dictionary containing signed transaction
            
        Signing Process:
        - Create wallet from mnemonic
        - Prepare signing context with extensions
        - Sign transaction with proper context
        - Validate signature
        """
        print("=== Signing Advanced Transaction ===")
        print("Signing transaction with context extensions...")
        
        if not self.ergo:
            print("⚠️  ergo-lib-python not available. This is a demonstration.")
            print("Context extensions included in signing:")
            for key, value in context_extensions.items():
                print(f"  {key}: {value[:20]}...")
            
            return {
                "signed_transaction": "demo_signed_advanced_tx",
                "transaction_id": "demo_advanced_tx_123",
                "context_extensions": context_extensions,
                "status": "demo"
            }
        
        # Actual implementation:
        # 1. Create wallet
        # wallet = self.ergo.Wallet.restore(wallet_mnemonic)
        # 
        # 2. Create signing context
        # signing_context = self.ergo.SigningContext()
        # 
        # # Add context extensions
        # for key, value in context_extensions.items():
        #     signing_context.add_extension(key, bytes.fromhex(value))
        # 
        # 3. Sign transaction
        # signed_tx = wallet.sign_transaction(transaction, signing_context)
        # 
        # 4. Get transaction ID
        # tx_id = signed_tx.id()
        
        print("✅ Advanced transaction signed successfully!")
        return {
            "signed": True,
            "transaction_id": "demo_advanced_tx_123",
            "context_extensions": context_extensions
        }
    
    def run_complete_example(self) -> None:
        """
        Run a complete advanced transaction example.
        
        This method demonstrates:
        1. Creating complex register data
        2. Building multiple outputs
        3. Adding context extensions
        4. Signing with extensions
        5. Broadcasting the transaction
        """
        print("🚀 Advanced Transaction Example")
        print("Demonstrating multiple outputs with registers and extensions")
        print("=" * 70)
        print()
        
        # Example addresses
        sender_address = "9fRusAarL1KkrWQVsxSRVYnvWzD4dWoLLxbYk3eWBV3jD3qvr3W"
        recipient1 = "9gQqZyxyjAptMbfW1Gydm3qaap11zd6X9DrABTbMBRJLjZhQRCA"
        recipient2 = "9h8UVJjdUYbNLuSqzZCqKNs2mxjVGYB9JwP4vVtNqmR3sKdxYyZ"
        
        # Step 1: Create register data for different outputs
        print("Step 1: Creating register data for outputs")
        print("-" * 40)
        
        # Output 1: Data storage box with multiple register types
        output1_registers = [
            RegisterData("R4", "String", "User Profile Data"),
            RegisterData("R5", "Int", 12345),
            RegisterData("R6", "Long", 1234567890123456789),
            RegisterData("R7", "Bytes", "deadbeef"),
        ]
        
        # Output 2: NFT-like box with metadata
        output2_registers = [
            RegisterData("R4", "String", "NFT Metadata"),
            RegisterData("R5", "String", json.dumps({
                "name": "My NFT",
                "description": "A unique digital asset",
                "image": "https://example.com/nft.png"
            })),
        ]
        
        # Define outputs
        outputs = [
            OutputSpec(
                recipient_address=recipient1,
                amount_nanoerg=2000000,  # 0.002 ERG
                registers=output1_registers
            ),
            OutputSpec(
                recipient_address=recipient2,
                amount_nanoerg=1500000,  # 0.0015 ERG
                registers=output2_registers
            )
        ]
        
        # Step 2: Create context extensions
        print("\nStep 2: Creating context extensions")
        print("-" * 40)
        
        metadata = {
            "transaction_type": "advanced_example",
            "version": "1.0",
            "timestamp": 1640995200,
            "user_data": {
                "action": "data_storage",
                "batch_id": "batch_001"
            }
        }
        
        context_extensions = self.create_context_extensions(metadata)
        print()
        
        # Step 3: Build the transaction
        print("Step 3: Building advanced transaction")
        print("-" * 40)
        
        transaction = self.build_advanced_transaction(
            sender_address=sender_address,
            outputs=outputs,
            context_extensions=context_extensions,
            fee_nanoerg=1000000
        )
        print()
        
        # Step 4: Sign the transaction
        print("Step 4: Signing transaction with context extensions")
        print("-" * 40)
        
        demo_mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
        signed_tx = self.sign_advanced_transaction(
            transaction=transaction,
            wallet_mnemonic=demo_mnemonic,
            context_extensions=context_extensions
        )
        print()
        
        # Step 5: Display transaction summary
        print("Step 5: Transaction Summary")
        print("-" * 40)
        
        if signed_tx.get("transaction_id"):
            print(f"✅ Transaction ID: {signed_tx['transaction_id']}")
            print(f"📦 Outputs: {len(outputs)}")
            print(f"🏷️  Total registers: {sum(len(output.registers) for output in outputs)}")
            print(f"🔧 Context extensions: {len(context_extensions)}")
            print()
            
            print("Output details:")
            for i, output in enumerate(outputs):
                print(f"  Output {i+1}:")
                print(f"    Recipient: {output.recipient_address}")
                print(f"    Amount: {output.amount_nanoerg} nanoERG")
                print(f"    Registers: {[r.register_id for r in output.registers]}")
            
            print("\nContext extensions:")
            for key in context_extensions.keys():
                print(f"    {key}")
        
        print("\n🎉 Advanced transaction example completed successfully!")
        print("\nKey concepts demonstrated:")
        print("1. ✅ Multiple outputs with different purposes")
        print("2. ✅ Register serialization for various data types")
        print("3. ✅ Context extensions for transaction metadata")
        print("4. ✅ Advanced transaction signing with context")
        print("5. ✅ Complex data structures in blockchain transactions")
        
        print("\nNext steps:")
        print("- Try modifying the register data types")
        print("- Add token transfers to outputs")
        print("- Experiment with different context extensions")
        print("- Implement smart contract interactions")


def main():
    """Run the advanced transaction example."""
    example = AdvancedTransactionExample()
    example.run_complete_example()


if __name__ == "__main__":
    main()