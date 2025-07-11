"""
Basic Wallet Tutorial - Learn fundamental wallet operations

This tutorial covers:
1. Creating a new wallet
2. Restoring a wallet from mnemonic
3. Generating addresses
4. Checking wallet balance
5. Basic security practices

Note: This tutorial requires ergo-lib-python to be installed.
Install it with: pip install ergo-lib-python
"""

from typing import List, Optional, Dict, Any
import logging


class BasicWalletTutorial:
    """
    Interactive tutorial for basic wallet operations in Ergo.
    
    This class provides step-by-step methods to learn wallet management,
    with detailed explanations and error handling for beginners.
    """
    
    def __init__(self, network: str = "mainnet"):
        """
        Initialize the wallet tutorial.
        
        Args:
            network: Network to use ("mainnet" or "testnet")
        """
        self.network = network
        self.logger = logging.getLogger(__name__)
        
        # Try to import ergo-lib-python
        try:
            # Note: These imports would work with actual ergo-lib-python
            # import ergo_lib_python as ergo
            # self.ergo = ergo
            pass
        except ImportError:
            self.logger.warning(
                "ergo-lib-python not found. Install it with: pip install ergo-lib-python"
            )
            self.ergo = None
    
    def step_1_create_new_wallet(self) -> Dict[str, Any]:
        """
        Step 1: Create a new wallet with a random mnemonic phrase.
        
        Returns:
            Dict containing wallet information and mnemonic
            
        Tutorial Notes:
        - A mnemonic phrase is a human-readable backup of your wallet
        - Keep your mnemonic phrase secure and never share it
        - The mnemonic can restore your entire wallet
        """
        print("=== Step 1: Creating a New Wallet ===")
        print("In this step, we'll create a new wallet with a random mnemonic phrase.")
        print("A mnemonic phrase is a series of words that can restore your wallet.")
        print()
        
        if not self.ergo:
            print("⚠️  ergo-lib-python not available. This is a demonstration.")
            # Simulated output for tutorial purposes
            return {
                "mnemonic": "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about",
                "addresses": ["9fRusAarL1KkrWQVsxSRVYnvWzD4dWoLLxbYk3eWBV3jD3qvr3W"],
                "status": "demo"
            }
        
        # Actual implementation would use ergo-lib-python:
        # wallet = self.ergo.Wallet.new_random()
        # mnemonic = wallet.mnemonic()
        # addresses = wallet.get_addresses()
        
        print("✅ Wallet created successfully!")
        print("💡 Important: Save your mnemonic phrase securely!")
        return {}
    
    def step_2_restore_wallet(self, mnemonic: str) -> Dict[str, Any]:
        """
        Step 2: Restore a wallet from a mnemonic phrase.
        
        Args:
            mnemonic: The mnemonic phrase to restore from
            
        Returns:
            Dict containing restored wallet information
            
        Tutorial Notes:
        - Always validate mnemonic phrases before use
        - A valid mnemonic follows BIP39 standard
        - Each mnemonic generates the same addresses every time
        """
        print("=== Step 2: Restoring a Wallet ===")
        print("In this step, we'll restore a wallet from a mnemonic phrase.")
        print(f"Using mnemonic: {mnemonic[:20]}...")
        print()
        
        if not self.ergo:
            print("⚠️  ergo-lib-python not available. This is a demonstration.")
            return {
                "addresses": ["9fRusAarL1KkrWQVsxSRVYnvWzD4dWoLLxbYk3eWBV3jD3qvr3W"],
                "status": "demo"
            }
        
        # Actual implementation:
        # wallet = self.ergo.Wallet.restore(mnemonic)
        # addresses = wallet.get_addresses()
        
        print("✅ Wallet restored successfully!")
        return {}
    
    def step_3_generate_addresses(self, count: int = 1) -> List[str]:
        """
        Step 3: Generate new addresses for the wallet.
        
        Args:
            count: Number of addresses to generate
            
        Returns:
            List of generated addresses
            
        Tutorial Notes:
        - Each address can receive funds independently
        - Addresses are derived from your wallet's master key
        - It's safe to generate many addresses
        """
        print("=== Step 3: Generating Addresses ===")
        print(f"Generating {count} new address(es)...")
        print()
        
        if not self.ergo:
            print("⚠️  ergo-lib-python not available. This is a demonstration.")
            return [f"9demo_address_{i}" for i in range(count)]
        
        # Actual implementation:
        # addresses = []
        # for i in range(count):
        #     address = wallet.get_new_address()
        #     addresses.append(address)
        
        print("✅ Addresses generated successfully!")
        return []
    
    def step_4_check_balance(self, address: str) -> Dict[str, Any]:
        """
        Step 4: Check the balance of an address.
        
        Args:
            address: The address to check balance for
            
        Returns:
            Dict containing balance information
            
        Tutorial Notes:
        - Balance is returned in nanoERG (1 ERG = 1,000,000,000 nanoERG)
        - You need to connect to an Ergo node to check real balances
        - This example shows how to format the results
        """
        print("=== Step 4: Checking Balance ===")
        print(f"Checking balance for address: {address}")
        print()
        
        if not self.ergo:
            print("⚠️  ergo-lib-python not available. This is a demonstration.")
            return {
                "balance_nanoerg": 1000000000,  # 1 ERG
                "balance_erg": 1.0,
                "status": "demo"
            }
        
        # Actual implementation would query the blockchain:
        # balance = self.ergo.get_balance(address)
        # balance_erg = balance / 1_000_000_000
        
        print("✅ Balance retrieved successfully!")
        return {}
    
    def run_complete_tutorial(self) -> None:
        """
        Run the complete wallet tutorial with all steps.
        
        This method walks through all tutorial steps in sequence,
        demonstrating a complete wallet workflow.
        """
        print("🎓 Welcome to the Basic Wallet Tutorial!")
        print("This tutorial will teach you fundamental wallet operations.")
        print("=" * 60)
        print()
        
        # Step 1: Create wallet
        wallet_info = self.step_1_create_new_wallet()
        print()
        
        # Step 2: Restore wallet (using the created mnemonic)
        if wallet_info.get("mnemonic"):
            restored_info = self.step_2_restore_wallet(wallet_info["mnemonic"])
            print()
        
        # Step 3: Generate addresses
        addresses = self.step_3_generate_addresses(3)
        print()
        
        # Step 4: Check balance
        if addresses:
            balance_info = self.step_4_check_balance(addresses[0])
            print()
        
        print("🎉 Tutorial completed successfully!")
        print("Next steps:")
        print("1. Install ergo-lib-python: pip install ergo-lib-python")
        print("2. Try the TransactionTutorial")
        print("3. Explore the TokenTutorial")


def main():
    """Run the basic wallet tutorial."""
    tutorial = BasicWalletTutorial()
    tutorial.run_complete_tutorial()


if __name__ == "__main__":
    main()