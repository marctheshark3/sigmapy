"""
Network utilities for Ergo blockchain operations.

This module provides utility functions for network connectivity,
node selection, and network-related operations.
"""

from typing import Dict, List, Optional, Any
import requests
import time
import logging


class NetworkUtils:
    """Utilities for Ergo network operations."""
    
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
    
    @staticmethod
    def test_node_connectivity(
        node_url: str,
        timeout: int = 10
    ) -> Dict[str, Any]:
        """
        Test connectivity to an Ergo node.
        
        Args:
            node_url: Node URL to test
            timeout: Request timeout in seconds
            
        Returns:
            Connectivity test result
        """
        result = {
            'url': node_url,
            'reachable': False,
            'response_time': None,
            'height': None,
            'version': None,
            'error': None
        }
        
        try:
            start_time = time.time()
            
            response = requests.get(
                f"{node_url.rstrip('/')}/info",
                timeout=timeout
            )
            
            end_time = time.time()
            result['response_time'] = round(end_time - start_time, 3)
            
            if response.status_code == 200:
                info = response.json()
                result['reachable'] = True
                result['height'] = info.get('fullHeight', 0)
                result['version'] = info.get('appVersion', 'unknown')
            else:
                result['error'] = f"HTTP {response.status_code}"
                
        except requests.exceptions.RequestException as e:
            result['error'] = str(e)
        except Exception as e:
            result['error'] = f"Unexpected error: {e}"
        
        return result
    
    @staticmethod
    def find_best_node(
        network: str = "mainnet",
        custom_nodes: Optional[List[str]] = None,
        timeout: int = 10
    ) -> Optional[str]:
        """
        Find the best available node for a network.
        
        Args:
            network: Network type ("mainnet" or "testnet")
            custom_nodes: Custom node URLs to test
            timeout: Request timeout per node
            
        Returns:
            Best node URL or None if none available
        """
        nodes_to_test = custom_nodes or NetworkUtils.DEFAULT_NODES.get(network, [])
        
        best_node = None
        best_response_time = float('inf')
        
        for node_url in nodes_to_test:
            test_result = NetworkUtils.test_node_connectivity(node_url, timeout)
            
            if test_result['reachable']:
                response_time = test_result['response_time'] or float('inf')
                
                if response_time < best_response_time:
                    best_response_time = response_time
                    best_node = node_url
        
        return best_node
    
    @staticmethod
    def get_network_status(node_url: str) -> Dict[str, Any]:
        """
        Get comprehensive network status.
        
        Args:
            node_url: Node URL to query
            
        Returns:
            Network status information
        """
        status = {
            'node_url': node_url,
            'reachable': False,
            'synced': False,
            'height': 0,
            'peers': 0,
            'mempool_size': 0,
            'version': 'unknown'
        }
        
        try:
            # Get basic info
            info_response = requests.get(f"{node_url.rstrip('/')}/info", timeout=10)
            if info_response.status_code == 200:
                info = info_response.json()
                status['reachable'] = True
                status['height'] = info.get('fullHeight', 0)
                status['peers'] = info.get('peersCount', 0)
                status['version'] = info.get('appVersion', 'unknown')
                status['synced'] = info.get('isMining', False)
            
            # Get mempool size
            try:
                mempool_response = requests.get(
                    f"{node_url.rstrip('/')}/transactions/unconfirmed/size",
                    timeout=5
                )
                if mempool_response.status_code == 200:
                    mempool_data = mempool_response.json()
                    status['mempool_size'] = mempool_data.get('size', 0)
            except:
                pass  # Mempool info is optional
                
        except Exception as e:
            status['error'] = str(e)
        
        return status
    
    @staticmethod
    def check_transaction_in_mempool(
        node_url: str,
        tx_id: str
    ) -> bool:
        """
        Check if transaction is in mempool.
        
        Args:
            node_url: Node URL to query
            tx_id: Transaction ID to check
            
        Returns:
            True if transaction is in mempool
        """
        try:
            response = requests.get(
                f"{node_url.rstrip('/')}/transactions/unconfirmed/{tx_id}",
                timeout=10
            )
            return response.status_code == 200
        except:
            return False
    
    @staticmethod
    def wait_for_height(
        node_url: str,
        target_height: int,
        timeout_seconds: int = 300
    ) -> bool:
        """
        Wait for blockchain to reach a specific height.
        
        Args:
            node_url: Node URL to monitor
            target_height: Target block height
            timeout_seconds: Maximum time to wait
            
        Returns:
            True if height reached, False if timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout_seconds:
            try:
                response = requests.get(
                    f"{node_url.rstrip('/')}/info",
                    timeout=10
                )
                
                if response.status_code == 200:
                    info = response.json()
                    current_height = info.get('fullHeight', 0)
                    
                    if current_height >= target_height:
                        return True
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception:
                time.sleep(30)  # Continue waiting even if request fails
        
        return False
    
    @staticmethod
    def estimate_confirmation_time(
        network: str = "mainnet",
        confirmations: int = 1
    ) -> int:
        """
        Estimate time for transaction confirmations.
        
        Args:
            network: Network type
            confirmations: Number of confirmations needed
            
        Returns:
            Estimated time in seconds
        """
        # Ergo block time is approximately 2 minutes
        block_time_seconds = 120
        
        # Add some buffer for network variability
        buffer_factor = 1.5
        
        return int(confirmations * block_time_seconds * buffer_factor)
    
    @staticmethod
    def format_network_info(status: Dict[str, Any]) -> str:
        """
        Format network status for display.
        
        Args:
            status: Network status dictionary
            
        Returns:
            Formatted status string
        """
        if not status.get('reachable', False):
            return f"❌ Node unreachable: {status.get('error', 'Unknown error')}"
        
        info = f"✅ Node: {status['node_url']}\n"
        info += f"   Height: {status['height']:,}\n"
        info += f"   Peers: {status['peers']}\n"
        info += f"   Mempool: {status['mempool_size']} txs\n"
        info += f"   Version: {status['version']}\n"
        info += f"   Synced: {'✅' if status['synced'] else '⏳'}"
        
        return info