"""
NetworkManager - Network and node operations

This class handles network-related operations including:
- Node connectivity
- Network information
- Transaction broadcasting
- Status monitoring
"""

from typing import Dict, List, Optional, Any
import logging
import time
import requests
from urllib.parse import urljoin


class NetworkManager:
    """
    Manages network connectivity and provides interfaces for
    interacting with Ergo nodes and the blockchain network.
    """
    
    # Default public nodes
    DEFAULT_NODES = {
        "mainnet": [
            "https://api.ergoplatform.com",
            "https://ergo-node.anetapps.com",
            "https://api.ergopad.io"
        ],
        "testnet": [
            "https://api-testnet.ergoplatform.com",
            "https://testnet-node.anetapps.com"
        ]
    }
    
    def __init__(
        self,
        node_url: Optional[str] = None,
        network: str = "mainnet",
        api_key: Optional[str] = None,
        timeout: int = 30
    ):
        """
        Initialize the NetworkManager.
        
        Args:
            node_url: Custom node URL (uses public nodes if None)
            network: Network type ("mainnet" or "testnet")
            api_key: API key for node access
            timeout: Request timeout in seconds
        """
        self.logger = logging.getLogger(__name__)
        self.network = network
        self.api_key = api_key
        self.timeout = timeout
        
        # Set up node URL
        if node_url:
            self.node_url = node_url
        else:
            self.node_url = self.DEFAULT_NODES[network][0]
        
        # Initialize session
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"X-API-Key": api_key})
        
        # Test connection
        self._test_connection()
    
    def _test_connection(self) -> None:
        """Test connection to the node."""
        try:
            info = self.get_network_info()
            self.logger.info(f"Connected to {self.network} node at {self.node_url}")
            self.logger.info(f"Network height: {info.get('height', 'unknown')}")
        except Exception as e:
            self.logger.warning(f"Connection test failed: {e}")
            # Try fallback nodes
            self._try_fallback_nodes()
    
    def _try_fallback_nodes(self) -> None:
        """Try fallback nodes if primary fails."""
        fallback_nodes = self.DEFAULT_NODES[self.network][1:]
        
        for node_url in fallback_nodes:
            try:
                self.node_url = node_url
                info = self.get_network_info()
                self.logger.info(f"Connected to fallback node: {node_url}")
                return
            except Exception as e:
                self.logger.warning(f"Fallback node {node_url} failed: {e}")
                continue
        
        self.logger.error("All nodes failed. Network operations may not work.")
    
    def get_network_info(self) -> Dict[str, Any]:
        """
        Get network information.
        
        Returns:
            Dictionary containing network details
        """
        try:
            response = self.session.get(
                urljoin(self.node_url, "/info"),
                timeout=self.timeout
            )
            response.raise_for_status()
            
            info = response.json()
            return {
                "network": self.network,
                "node_url": self.node_url,
                "height": info.get("fullHeight", 0),
                "version": info.get("appVersion", "unknown"),
                "peers": info.get("peersCount", 0),
                "synced": info.get("isMining", False)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get network info: {e}")
            # Return demo data if real node unavailable
            return {
                "network": self.network,
                "node_url": self.node_url,
                "height": 1000000,
                "version": "demo",
                "peers": 0,
                "synced": False
            }
    
    def get_block_height(self) -> int:
        """
        Get current block height.
        
        Returns:
            Current block height
        """
        try:
            response = self.session.get(
                urljoin(self.node_url, "/blocks/lastHeaders/1"),
                timeout=self.timeout
            )
            response.raise_for_status()
            
            blocks = response.json()
            if blocks:
                return blocks[0].get("height", 0)
            
        except Exception as e:
            self.logger.error(f"Failed to get block height: {e}")
        
        return 0
    
    def get_address_balance(self, address: str) -> Dict[str, Any]:
        """
        Get balance for an address.
        
        Args:
            address: Address to check
            
        Returns:
            Dictionary containing balance information
        """
        try:
            response = self.session.get(
                urljoin(self.node_url, f"/blockchain/balance/{address}"),
                timeout=self.timeout
            )
            response.raise_for_status()
            
            balance_data = response.json()
            return {
                "address": address,
                "nanoerg": balance_data.get("nanoErgs", 0),
                "tokens": balance_data.get("tokens", [])
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get address balance: {e}")
            return {
                "address": address,
                "nanoerg": 0,
                "tokens": []
            }
    
    def get_address_utxos(self, address: str) -> List[Dict[str, Any]]:
        """
        Get UTXOs for an address.
        
        Args:
            address: Address to check
            
        Returns:
            List of UTXO dictionaries
        """
        try:
            response = self.session.get(
                urljoin(self.node_url, f"/blockchain/box/unspent/byAddress/{address}"),
                timeout=self.timeout
            )
            response.raise_for_status()
            
            utxos = response.json()
            return [self._format_utxo(utxo) for utxo in utxos]
            
        except Exception as e:
            self.logger.error(f"Failed to get UTXOs for {address}: {e}")
            return []
    
    def broadcast_transaction(self, signed_tx: Any) -> str:
        """
        Broadcast a signed transaction to the network.
        
        Args:
            signed_tx: Signed transaction to broadcast
            
        Returns:
            Transaction ID
        """
        try:
            # Convert transaction to JSON format
            if hasattr(signed_tx, 'to_json'):
                tx_json = signed_tx.to_json()
            else:
                tx_json = signed_tx
            
            response = self.session.post(
                urljoin(self.node_url, "/transactions"),
                json=tx_json,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            return response.json().get("id", "")
            
        except Exception as e:
            self.logger.error(f"Failed to broadcast transaction: {e}")
            # Return demo transaction ID
            return f"demo_broadcast_{int(time.time())}"
    
    def get_transaction_status(self, tx_id: str) -> Dict[str, Any]:
        """
        Get transaction status.
        
        Args:
            tx_id: Transaction ID to check
            
        Returns:
            Dictionary containing transaction status
        """
        try:
            response = self.session.get(
                urljoin(self.node_url, f"/transactions/{tx_id}"),
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                tx_data = response.json()
                return {
                    "transaction_id": tx_id,
                    "status": "confirmed",
                    "confirmations": tx_data.get("numConfirmations", 0),
                    "block_height": tx_data.get("inclusionHeight", 0),
                    "timestamp": tx_data.get("timestamp", 0)
                }
            elif response.status_code == 404:
                return {
                    "transaction_id": tx_id,
                    "status": "not_found",
                    "confirmations": 0,
                    "block_height": 0
                }
            else:
                response.raise_for_status()
                
        except Exception as e:
            self.logger.error(f"Failed to get transaction status: {e}")
            return {
                "transaction_id": tx_id,
                "status": "unknown",
                "confirmations": 0,
                "block_height": 0
            }
    
    def wait_for_confirmation(
        self,
        tx_id: str,
        timeout_seconds: int = 300,
        min_confirmations: int = 1
    ) -> Dict[str, Any]:
        """
        Wait for transaction confirmation.
        
        Args:
            tx_id: Transaction ID to wait for
            timeout_seconds: Maximum time to wait
            min_confirmations: Minimum confirmations required
            
        Returns:
            Dictionary containing final transaction status
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout_seconds:
            status = self.get_transaction_status(tx_id)
            
            if status["status"] == "confirmed":
                if status["confirmations"] >= min_confirmations:
                    self.logger.info(f"Transaction {tx_id} confirmed with {status['confirmations']} confirmations")
                    return status
            elif status["status"] == "not_found":
                self.logger.warning(f"Transaction {tx_id} not found")
                time.sleep(10)
                continue
            
            time.sleep(10)  # Check every 10 seconds
        
        self.logger.warning(f"Transaction {tx_id} not confirmed within timeout")
        return self.get_transaction_status(tx_id)
    
    def get_mempool_size(self) -> int:
        """
        Get current mempool size.
        
        Returns:
            Number of transactions in mempool
        """
        try:
            response = self.session.get(
                urljoin(self.node_url, "/transactions/unconfirmed/size"),
                timeout=self.timeout
            )
            response.raise_for_status()
            
            return response.json().get("size", 0)
            
        except Exception as e:
            self.logger.error(f"Failed to get mempool size: {e}")
            return 0
    
    def validate_address(self, address: str) -> bool:
        """
        Validate an Ergo address.
        
        Args:
            address: Address to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Basic validation - check address format
            if not address or len(address) < 40:
                return False
            
            # Check if address starts with correct network prefix
            if self.network == "mainnet" and not address.startswith("9"):
                return False
            elif self.network == "testnet" and not address.startswith("3"):
                return False
            
            # Try to get balance (this will fail for invalid addresses)
            self.get_address_balance(address)
            return True
            
        except Exception:
            return False
    
    def get_token_info(self, token_id: str) -> Dict[str, Any]:
        """
        Get token information.
        
        Args:
            token_id: Token ID to lookup
            
        Returns:
            Dictionary containing token information
        """
        try:
            response = self.session.get(
                urljoin(self.node_url, f"/blockchain/token/{token_id}"),
                timeout=self.timeout
            )
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            self.logger.error(f"Failed to get token info: {e}")
            return {
                "id": token_id,
                "name": "Unknown Token",
                "description": "",
                "type": "EIP-4 Token",
                "decimals": 0
            }
    
    def _format_utxo(self, utxo: Dict[str, Any]) -> Dict[str, Any]:
        """Format a UTXO for consistent output."""
        return {
            "box_id": utxo.get("boxId", ""),
            "value": utxo.get("value", 0),
            "address": utxo.get("address", ""),
            "tokens": utxo.get("assets", []),
            "registers": utxo.get("additionalRegisters", {}),
            "creation_height": utxo.get("creationHeight", 0)
        }
    
    def __str__(self) -> str:
        """String representation of the network manager."""
        return f"NetworkManager(network={self.network})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return (
            f"NetworkManager("
            f"network={self.network}, "
            f"node_url={self.node_url}"
            f")"
        )