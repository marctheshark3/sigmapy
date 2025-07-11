"""
Environment utilities for SigmaPy configuration

This module provides utilities for loading configuration from environment
variables and .env files, ensuring secure handling of sensitive data.
"""

import os
import logging
from typing import Optional, Dict, Any, Union
from pathlib import Path


class EnvManager:
    """
    Environment configuration manager for SigmaPy.
    
    This class handles loading configuration from environment variables
    and .env files, with security best practices for sensitive data.
    """
    
    def __init__(self, env_file: Optional[Union[str, Path]] = None):
        """
        Initialize EnvManager.
        
        Args:
            env_file: Path to .env file (defaults to .env in current directory)
        """
        self.logger = logging.getLogger(__name__)
        self.env_file = env_file or Path.cwd() / ".env"
        self.loaded_vars = {}
        
        # Load .env file if it exists
        self._load_env_file()
    
    def _load_env_file(self) -> None:
        """Load environment variables from .env file."""
        if not isinstance(self.env_file, Path):
            self.env_file = Path(self.env_file)
        
        if not self.env_file.exists():
            self.logger.debug(f"No .env file found at {self.env_file}")
            return
        
        try:
            with open(self.env_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse key=value pairs
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Remove quotes if present
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        
                        # Set environment variable if not already set
                        if key not in os.environ:
                            os.environ[key] = value
                            self.loaded_vars[key] = value
                            self.logger.debug(f"Loaded {key} from .env file")
                        else:
                            self.logger.debug(f"Skipped {key} (already set in environment)")
                    else:
                        self.logger.warning(f"Invalid line format in .env file at line {line_num}: {line}")
        
        except Exception as e:
            self.logger.error(f"Failed to load .env file: {e}")
    
    def get_seed_phrase(self) -> Optional[str]:
        """
        Get wallet seed phrase from environment.
        
        Returns:
            Seed phrase string or None if not found
            
        Environment variables checked (in order):
        - SIGMAPY_SEED_PHRASE
        - WALLET_SEED_PHRASE
        - SEED_PHRASE
        """
        seed_phrase_vars = [
            "SIGMAPY_SEED_PHRASE",
            "WALLET_SEED_PHRASE", 
            "SEED_PHRASE"
        ]
        
        for var in seed_phrase_vars:
            value = os.getenv(var)
            if value:
                # Basic validation
                if self._validate_seed_phrase(value):
                    return value
                else:
                    self.logger.warning(f"Invalid seed phrase format in {var}")
        
        return None
    
    def get_network(self) -> str:
        """
        Get network configuration from environment.
        
        Returns:
            Network name ("mainnet" or "testnet")
        """
        network = os.getenv("SIGMAPY_NETWORK", "testnet").lower()
        if network not in ["mainnet", "testnet"]:
            self.logger.warning(f"Invalid network '{network}', defaulting to testnet")
            return "testnet"
        return network
    
    def get_node_url(self) -> Optional[str]:
        """
        Get node URL from environment.
        
        Returns:
            Node URL string or None for default
        """
        return os.getenv("SIGMAPY_NODE_URL") or None
    
    def get_api_key(self) -> Optional[str]:
        """
        Get API key from environment.
        
        Returns:
            API key string or None if not set
        """
        return os.getenv("SIGMAPY_API_KEY") or None
    
    def get_demo_mode(self) -> bool:
        """
        Get demo mode setting from environment.
        
        Returns:
            True if demo mode is enabled, False otherwise
        """
        demo_mode = os.getenv("SIGMAPY_DEMO_MODE", "false").lower()
        return demo_mode in ["true", "1", "yes", "on"]
    
    def get_timeout(self) -> int:
        """
        Get network timeout from environment.
        
        Returns:
            Timeout in seconds
        """
        try:
            timeout = int(os.getenv("SIGMAPY_TIMEOUT", "30"))
            if timeout <= 0:
                raise ValueError("Timeout must be positive")
            return timeout
        except (ValueError, TypeError):
            self.logger.warning("Invalid timeout value, using default 30 seconds")
            return 30
    
    def get_batch_size(self) -> int:
        """
        Get default batch size from environment.
        
        Returns:
            Batch size for operations
        """
        try:
            batch_size = int(os.getenv("SIGMAPY_BATCH_SIZE", "50"))
            if batch_size <= 0:
                raise ValueError("Batch size must be positive")
            return batch_size
        except (ValueError, TypeError):
            self.logger.warning("Invalid batch size value, using default 50")
            return 50
    
    def get_default_fee(self) -> float:
        """
        Get default transaction fee from environment.
        
        Returns:
            Default fee in ERG
        """
        try:
            fee = float(os.getenv("SIGMAPY_DEFAULT_FEE", "0.001"))
            if fee <= 0:
                raise ValueError("Fee must be positive")
            return fee
        except (ValueError, TypeError):
            self.logger.warning("Invalid fee value, using default 0.001 ERG")
            return 0.001
    
    def get_log_level(self) -> str:
        """
        Get logging level from environment.
        
        Returns:
            Log level string
        """
        level = os.getenv("SIGMAPY_LOG_LEVEL", "INFO").upper()
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if level not in valid_levels:
            self.logger.warning(f"Invalid log level '{level}', using INFO")
            return "INFO"
        return level
    
    def get_log_file(self) -> Optional[str]:
        """
        Get log file path from environment.
        
        Returns:
            Log file path or None for console only
        """
        return os.getenv("SIGMAPY_LOG_FILE") or None
    
    def get_require_confirmation(self) -> bool:
        """
        Get transaction confirmation requirement from environment.
        
        Returns:
            True if confirmation is required, False otherwise
        """
        confirmation = os.getenv("SIGMAPY_REQUIRE_CONFIRMATION", "true").lower()
        return confirmation in ["true", "1", "yes", "on"]
    
    def get_max_retry_attempts(self) -> int:
        """
        Get maximum retry attempts from environment.
        
        Returns:
            Maximum retry attempts
        """
        try:
            attempts = int(os.getenv("SIGMAPY_MAX_RETRY_ATTEMPTS", "3"))
            if attempts < 0:
                raise ValueError("Retry attempts must be non-negative")
            return attempts
        except (ValueError, TypeError):
            self.logger.warning("Invalid retry attempts value, using default 3")
            return 3
    
    def get_config_dict(self) -> Dict[str, Any]:
        """
        Get all configuration as a dictionary.
        
        Returns:
            Dictionary containing all configuration values
        """
        return {
            "seed_phrase": self.get_seed_phrase(),
            "network": self.get_network(),
            "node_url": self.get_node_url(),
            "api_key": self.get_api_key(),
            "demo_mode": self.get_demo_mode(),
            "timeout": self.get_timeout(),
            "batch_size": self.get_batch_size(),
            "default_fee": self.get_default_fee(),
            "log_level": self.get_log_level(),
            "log_file": self.get_log_file(),
            "require_confirmation": self.get_require_confirmation(),
            "max_retry_attempts": self.get_max_retry_attempts(),
        }
    
    def _validate_seed_phrase(self, seed_phrase: str) -> bool:
        """
        Validate seed phrase format.
        
        Args:
            seed_phrase: Seed phrase to validate
            
        Returns:
            True if valid format, False otherwise
        """
        if not seed_phrase or not isinstance(seed_phrase, str):
            return False
        
        # Check word count
        words = seed_phrase.split()
        if len(words) not in [12, 15, 18, 21, 24]:
            return False
        
        # Check for common test phrases (should not be used in production)
        test_phrases = [
            "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about",
            "test test test test test test test test test test test test"
        ]
        
        if seed_phrase in test_phrases:
            if self.get_network() == "mainnet":
                self.logger.error("Test seed phrase detected on mainnet! This is dangerous!")
                return False
            else:
                self.logger.warning("Using test seed phrase on testnet")
        
        return True
    
    def create_env_file(self, overwrite: bool = False) -> None:
        """
        Create a .env file with default values.
        
        Args:
            overwrite: Whether to overwrite existing file
        """
        if self.env_file.exists() and not overwrite:
            self.logger.warning(f".env file already exists at {self.env_file}")
            return
        
        env_content = '''# SigmaPy Environment Configuration
# Copy this file to .env and fill in your actual values
# NEVER commit your .env file to git!

# Wallet Configuration
SIGMAPY_SEED_PHRASE="your twelve word mnemonic seed phrase goes here for wallet operations"

# Network Configuration
SIGMAPY_NETWORK="testnet"  # or "mainnet" for production
SIGMAPY_NODE_URL=""  # Optional: custom node URL (leave empty for default public nodes)
SIGMAPY_API_KEY=""   # Optional: API key for node access

# Demo Configuration (for testing without real wallet)
SIGMAPY_DEMO_MODE="true"  # Set to "false" to use real wallet operations

# Advanced Configuration
SIGMAPY_TIMEOUT="30"      # Network timeout in seconds
SIGMAPY_BATCH_SIZE="50"   # Default batch size for operations
SIGMAPY_DEFAULT_FEE="0.001"  # Default transaction fee in ERG

# Logging Configuration
SIGMAPY_LOG_LEVEL="INFO"  # DEBUG, INFO, WARNING, ERROR
SIGMAPY_LOG_FILE=""       # Optional: log file path (leave empty for console only)

# Security Configuration
SIGMAPY_REQUIRE_CONFIRMATION="true"  # Require confirmation for transactions
SIGMAPY_MAX_RETRY_ATTEMPTS="3"       # Maximum retry attempts for failed operations
'''
        
        try:
            with open(self.env_file, 'w', encoding='utf-8') as f:
                f.write(env_content)
            self.logger.info(f"Created .env file at {self.env_file}")
        except Exception as e:
            self.logger.error(f"Failed to create .env file: {e}")
    
    def validate_security(self) -> Dict[str, Any]:
        """
        Validate security configuration.
        
        Returns:
            Dictionary with security validation results
        """
        issues = []
        warnings = []
        
        # Check seed phrase security
        seed_phrase = self.get_seed_phrase()
        if seed_phrase:
            if seed_phrase in ["abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"]:
                if self.get_network() == "mainnet":
                    issues.append("Using test seed phrase on mainnet is extremely dangerous!")
                else:
                    warnings.append("Using test seed phrase on testnet")
            
            # Check if seed phrase is too short
            if len(seed_phrase.split()) < 12:
                issues.append("Seed phrase appears to be too short (less than 12 words)")
        
        # Check network configuration
        network = self.get_network()
        if network == "mainnet":
            if not seed_phrase:
                issues.append("No seed phrase configured for mainnet operations")
            
            if self.get_demo_mode():
                warnings.append("Demo mode is enabled on mainnet")
        
        # Check if .env file exists and is secure
        if self.env_file.exists():
            try:
                # Check file permissions (Unix-like systems)
                import stat
                file_stat = self.env_file.stat()
                if file_stat.st_mode & stat.S_IROTH:
                    warnings.append(".env file is readable by others")
                if file_stat.st_mode & stat.S_IWOTH:
                    issues.append(".env file is writable by others")
            except Exception:
                pass  # Skip permission check on Windows or other systems
        
        return {
            "issues": issues,
            "warnings": warnings,
            "secure": len(issues) == 0
        }
    
    def __str__(self) -> str:
        """String representation of EnvManager."""
        return f"EnvManager(env_file={self.env_file})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"EnvManager(env_file={self.env_file}, loaded_vars={len(self.loaded_vars)})"


# Global instance for easy access
env_manager = EnvManager()


def get_env_config() -> Dict[str, Any]:
    """
    Get environment configuration using the global EnvManager.
    
    Returns:
        Dictionary containing all configuration values
    """
    return env_manager.get_config_dict()


def get_seed_phrase() -> Optional[str]:
    """
    Get seed phrase from environment using the global EnvManager.
    
    Returns:
        Seed phrase string or None if not found
    """
    return env_manager.get_seed_phrase()


def validate_env_security() -> Dict[str, Any]:
    """
    Validate environment security using the global EnvManager.
    
    Returns:
        Dictionary with security validation results
    """
    return env_manager.validate_security()


def main():
    """Demonstrate environment utilities."""
    print("🔐 Environment Configuration Demo")
    print("=" * 50)
    
    # Create EnvManager
    env_mgr = EnvManager()
    
    # Show configuration
    config = env_mgr.get_config_dict()
    print("\n📋 Current Configuration:")
    for key, value in config.items():
        if key == "seed_phrase" and value:
            # Don't show full seed phrase for security
            display_value = value[:20] + "..." if len(value) > 20 else value
        else:
            display_value = value
        print(f"   {key}: {display_value}")
    
    # Validate security
    security = env_mgr.validate_security()
    print(f"\n🔐 Security Status: {'✅ Secure' if security['secure'] else '❌ Issues Found'}")
    
    if security['issues']:
        print("\n❌ Security Issues:")
        for issue in security['issues']:
            print(f"   - {issue}")
    
    if security['warnings']:
        print("\n⚠️  Security Warnings:")
        for warning in security['warnings']:
            print(f"   - {warning}")
    
    # Show .env file status
    print(f"\n📄 .env File: {env_mgr.env_file}")
    if env_mgr.env_file.exists():
        print(f"   ✅ Exists ({len(env_mgr.loaded_vars)} variables loaded)")
    else:
        print("   ❌ Not found")
        print("   💡 Run env_mgr.create_env_file() to create one")


if __name__ == "__main__":
    main()