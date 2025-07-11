"""
Serialization utilities for Ergo blockchain data structures

This module provides helper functions for:
- Serializing data for ErgoBox registers
- Handling different Sigma types
- Context extension serialization
- Data type conversions and validation
"""

from typing import Union, Any, Dict, List
import json
import struct
from dataclasses import dataclass
from enum import Enum


class SigmaType(Enum):
    """Sigma protocol data types for serialization."""
    BOOLEAN = 1
    BYTE = 2
    SHORT = 3
    INT = 4
    LONG = 5
    BIG_INT = 6
    GROUP_ELEMENT = 7
    SIGMA_PROP = 8
    BOX = 9
    AVL_TREE = 10
    OPTION = 11
    COLL_BYTE = 12
    COLL_INT = 13
    COLL_LONG = 14
    TUPLE = 15


@dataclass
class SerializedData:
    """Container for serialized data with metadata."""
    data_type: SigmaType
    original_value: Any
    serialized_hex: str
    size_bytes: int


class SerializationUtils:
    """
    Utility class for serializing data for Ergo blockchain operations.
    
    This class provides methods to serialize various data types according
    to the Sigma protocol specification for use in ErgoBox registers and
    context extensions.
    """
    
    @staticmethod
    def serialize_int(value: int) -> SerializedData:
        """
        Serialize an integer value.
        
        Args:
            value: Integer value to serialize
            
        Returns:
            SerializedData object with hex representation
            
        Examples:
            >>> result = SerializationUtils.serialize_int(12345)
            >>> result.serialized_hex
            '0400003039'
        """
        if not isinstance(value, int):
            raise TypeError("Value must be an integer")
        
        if value < -2**31 or value >= 2**31:
            raise ValueError("Integer value out of range for 32-bit signed integer")
        
        # Sigma type prefix (04 for Int) + 4 bytes for value
        packed = struct.pack('>I', value & 0xFFFFFFFF)
        serialized_hex = f"04{packed.hex()}"
        
        return SerializedData(
            data_type=SigmaType.INT,
            original_value=value,
            serialized_hex=serialized_hex,
            size_bytes=5
        )
    
    @staticmethod
    def serialize_long(value: int) -> SerializedData:
        """
        Serialize a long integer value.
        
        Args:
            value: Long integer value to serialize
            
        Returns:
            SerializedData object with hex representation
            
        Examples:
            >>> result = SerializationUtils.serialize_long(1234567890123456789)
            >>> result.serialized_hex
            '0511223344556677889'
        """
        if not isinstance(value, int):
            raise TypeError("Value must be an integer")
        
        if value < -2**63 or value >= 2**63:
            raise ValueError("Long value out of range for 64-bit signed integer")
        
        # Sigma type prefix (05 for Long) + 8 bytes for value
        packed = struct.pack('>Q', value & 0xFFFFFFFFFFFFFFFF)
        serialized_hex = f"05{packed.hex()}"
        
        return SerializedData(
            data_type=SigmaType.LONG,
            original_value=value,
            serialized_hex=serialized_hex,
            size_bytes=9
        )
    
    @staticmethod
    def serialize_boolean(value: bool) -> SerializedData:
        """
        Serialize a boolean value.
        
        Args:
            value: Boolean value to serialize
            
        Returns:
            SerializedData object with hex representation
            
        Examples:
            >>> result = SerializationUtils.serialize_boolean(True)
            >>> result.serialized_hex
            '0101'
        """
        if not isinstance(value, bool):
            raise TypeError("Value must be a boolean")
        
        # Sigma type prefix (01 for Boolean) + 1 byte for value
        serialized_hex = f"01{'01' if value else '00'}"
        
        return SerializedData(
            data_type=SigmaType.BOOLEAN,
            original_value=value,
            serialized_hex=serialized_hex,
            size_bytes=2
        )
    
    @staticmethod
    def serialize_byte_array(value: Union[bytes, str]) -> SerializedData:
        """
        Serialize a byte array or string.
        
        Args:
            value: Bytes or string to serialize
            
        Returns:
            SerializedData object with hex representation
            
        Examples:
            >>> result = SerializationUtils.serialize_byte_array(b"Hello")
            >>> result.serialized_hex
            '0c0548656c6c6f'
        """
        if isinstance(value, str):
            byte_data = value.encode('utf-8')
        elif isinstance(value, bytes):
            byte_data = value
        else:
            raise TypeError("Value must be bytes or string")
        
        if len(byte_data) > 255:
            raise ValueError("Byte array too long (max 255 bytes)")
        
        # Sigma type prefix (0c for Coll[Byte]) + length + data
        length_hex = f"{len(byte_data):02x}"
        data_hex = byte_data.hex()
        serialized_hex = f"0c{length_hex}{data_hex}"
        
        return SerializedData(
            data_type=SigmaType.COLL_BYTE,
            original_value=value,
            serialized_hex=serialized_hex,
            size_bytes=2 + len(byte_data)
        )
    
    @staticmethod
    def serialize_hex_string(hex_string: str) -> SerializedData:
        """
        Serialize a hex string as byte array.
        
        Args:
            hex_string: Hex string to serialize (without 0x prefix)
            
        Returns:
            SerializedData object with hex representation
            
        Examples:
            >>> result = SerializationUtils.serialize_hex_string("deadbeef")
            >>> result.serialized_hex
            '0c04deadbeef'
        """
        if not isinstance(hex_string, str):
            raise TypeError("Value must be a string")
        
        # Remove 0x prefix if present
        if hex_string.startswith("0x"):
            hex_string = hex_string[2:]
        
        # Validate hex string
        try:
            byte_data = bytes.fromhex(hex_string)
        except ValueError:
            raise ValueError("Invalid hex string")
        
        if len(byte_data) > 255:
            raise ValueError("Hex data too long (max 255 bytes)")
        
        # Sigma type prefix (0c for Coll[Byte]) + length + data
        length_hex = f"{len(byte_data):02x}"
        serialized_hex = f"0c{length_hex}{hex_string}"
        
        return SerializedData(
            data_type=SigmaType.COLL_BYTE,
            original_value=hex_string,
            serialized_hex=serialized_hex,
            size_bytes=2 + len(byte_data)
        )
    
    @staticmethod
    def serialize_json(value: Union[Dict, List, str]) -> SerializedData:
        """
        Serialize JSON data as byte array.
        
        Args:
            value: JSON-serializable data structure
            
        Returns:
            SerializedData object with hex representation
            
        Examples:
            >>> data = {"name": "Alice", "age": 30}
            >>> result = SerializationUtils.serialize_json(data)
            >>> result.data_type
            SigmaType.COLL_BYTE
        """
        if isinstance(value, str):
            json_string = value
        else:
            json_string = json.dumps(value, separators=(',', ':'))
        
        return SerializationUtils.serialize_byte_array(json_string)
    
    @staticmethod
    def serialize_for_register(register_id: str, value: Any, data_type: str = None) -> str:
        """
        Serialize data for a specific ErgoBox register.
        
        Args:
            register_id: Register ID (R4, R5, R6, R7, R8, R9)
            value: Value to serialize
            data_type: Optional type hint for serialization
            
        Returns:
            Hex string suitable for register storage
            
        Examples:
            >>> hex_data = SerializationUtils.serialize_for_register("R4", 12345, "Int")
            >>> hex_data
            '0400003039'
        """
        if register_id not in ["R4", "R5", "R6", "R7", "R8", "R9"]:
            raise ValueError(f"Invalid register ID: {register_id}")
        
        # Auto-detect type if not specified
        if data_type is None:
            if isinstance(value, bool):
                data_type = "Boolean"
            elif isinstance(value, int):
                if -2**31 <= value < 2**31:
                    data_type = "Int"
                else:
                    data_type = "Long"
            elif isinstance(value, str):
                data_type = "String"
            elif isinstance(value, bytes):
                data_type = "Bytes"
            elif isinstance(value, (dict, list)):
                data_type = "JSON"
            else:
                raise TypeError(f"Cannot auto-detect type for value: {type(value)}")
        
        # Serialize based on type
        if data_type == "Boolean":
            result = SerializationUtils.serialize_boolean(value)
        elif data_type == "Int":
            result = SerializationUtils.serialize_int(value)
        elif data_type == "Long":
            result = SerializationUtils.serialize_long(value)
        elif data_type == "String":
            result = SerializationUtils.serialize_byte_array(value)
        elif data_type == "Bytes":
            if isinstance(value, str):
                result = SerializationUtils.serialize_hex_string(value)
            else:
                result = SerializationUtils.serialize_byte_array(value)
        elif data_type == "JSON":
            result = SerializationUtils.serialize_json(value)
        else:
            raise ValueError(f"Unsupported data type: {data_type}")
        
        return result.serialized_hex
    
    @staticmethod
    def serialize_context_extension(key: str, value: Any) -> str:
        """
        Serialize data for context extension.
        
        Args:
            key: Extension key
            value: Value to serialize
            
        Returns:
            Hex string suitable for context extension
            
        Examples:
            >>> hex_data = SerializationUtils.serialize_context_extension("user_id", 12345)
            >>> hex_data
            '0400003039'
        """
        return SerializationUtils.serialize_for_register("R4", value)  # Use same logic
    
    @staticmethod
    def create_register_map(register_data: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Create a map of register IDs to serialized data.
        
        Args:
            register_data: List of register specifications
            
        Returns:
            Dictionary mapping register IDs to hex strings
            
        Examples:
            >>> data = [
            ...     {"register": "R4", "value": 12345, "type": "Int"},
            ...     {"register": "R5", "value": "Hello", "type": "String"}
            ... ]
            >>> result = SerializationUtils.create_register_map(data)
            >>> result["R4"]
            '0400003039'
        """
        register_map = {}
        
        for item in register_data:
            register_id = item["register"]
            value = item["value"]
            data_type = item.get("type")
            
            serialized = SerializationUtils.serialize_for_register(
                register_id, value, data_type
            )
            register_map[register_id] = serialized
        
        return register_map
    
    @staticmethod
    def create_extension_map(extension_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Create a map of context extension keys to serialized data.
        
        Args:
            extension_data: Dictionary of extension data
            
        Returns:
            Dictionary mapping extension keys to hex strings
            
        Examples:
            >>> data = {"user_id": 12345, "action": "transfer"}
            >>> result = SerializationUtils.create_extension_map(data)
            >>> result["user_id"]
            '0400003039'
        """
        extension_map = {}
        
        for key, value in extension_data.items():
            serialized = SerializationUtils.serialize_context_extension(key, value)
            extension_map[key] = serialized
        
        return extension_map
    
    @staticmethod
    def validate_serialized_data(hex_string: str) -> bool:
        """
        Validate serialized data format.
        
        Args:
            hex_string: Hex string to validate
            
        Returns:
            True if valid, False otherwise
            
        Examples:
            >>> SerializationUtils.validate_serialized_data("0400003039")
            True
            >>> SerializationUtils.validate_serialized_data("invalid")
            False
        """
        try:
            # Check if it's valid hex
            bytes.fromhex(hex_string)
            
            # Check minimum length (type prefix + at least 1 byte)
            if len(hex_string) < 4:
                return False
            
            # Check if type prefix is valid
            type_prefix = hex_string[:2]
            valid_prefixes = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "0a", "0b", "0c", "0d", "0e", "0f"]
            
            return type_prefix in valid_prefixes
            
        except ValueError:
            return False


def main():
    """Demonstrate serialization utilities."""
    print("🔧 Serialization Utilities Demo")
    print("=" * 50)
    
    # Test different data types
    test_cases = [
        ("Boolean", True),
        ("Int", 12345),
        ("Long", 1234567890123456789),
        ("String", "Hello, Ergo!"),
        ("Hex", "deadbeef"),
        ("JSON", {"name": "Alice", "age": 30, "active": True}),
    ]
    
    print("\n1. Basic serialization tests:")
    for data_type, value in test_cases:
        try:
            if data_type == "Boolean":
                result = SerializationUtils.serialize_boolean(value)
            elif data_type == "Int":
                result = SerializationUtils.serialize_int(value)
            elif data_type == "Long":
                result = SerializationUtils.serialize_long(value)
            elif data_type == "String":
                result = SerializationUtils.serialize_byte_array(value)
            elif data_type == "Hex":
                result = SerializationUtils.serialize_hex_string(value)
            elif data_type == "JSON":
                result = SerializationUtils.serialize_json(value)
            
            print(f"   {data_type:8} | {str(value):30} | {result.serialized_hex}")
            
        except Exception as e:
            print(f"   {data_type:8} | {str(value):30} | ERROR: {e}")
    
    print("\n2. Register serialization:")
    register_data = [
        {"register": "R4", "value": 12345, "type": "Int"},
        {"register": "R5", "value": "User Profile", "type": "String"},
        {"register": "R6", "value": {"id": 123, "name": "Alice"}, "type": "JSON"},
    ]
    
    register_map = SerializationUtils.create_register_map(register_data)
    for reg_id, hex_data in register_map.items():
        print(f"   {reg_id}: {hex_data}")
    
    print("\n3. Context extension serialization:")
    extension_data = {
        "transaction_type": "data_storage",
        "user_id": 12345,
        "metadata": {"version": "1.0", "batch": "001"}
    }
    
    extension_map = SerializationUtils.create_extension_map(extension_data)
    for key, hex_data in extension_map.items():
        print(f"   {key}: {hex_data}")
    
    print("\n4. Validation tests:")
    test_hex = [
        "0400003039",  # Valid int
        "0c0548656c6c6f",  # Valid string
        "invalid",  # Invalid hex
        "01",  # Too short
    ]
    
    for hex_string in test_hex:
        valid = SerializationUtils.validate_serialized_data(hex_string)
        print(f"   {hex_string:15} | {'Valid' if valid else 'Invalid'}")


if __name__ == "__main__":
    main()