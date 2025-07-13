"""
RoyaltyManager - Complex multi-recipient royalty structure management

This class provides methods for:
- Creating complex royalty structures with multiple recipients
- Validating royalty percentages and distributions
- EIP-24 compliant royalty encoding
- Royalty calculation and distribution utilities

Based on EIP-24 Artwork Contract standard:
https://docs.ergoplatform.com/dev/tokens/standards/eip24/
"""

from typing import Dict, List, Optional, Any, Union
import logging
from decimal import Decimal

from ..utils import AmountUtils


class RoyaltyManager:
    """
    Royalty structure management with EIP-24 compliance.
    
    This class provides utilities for creating, validating, and managing
    complex royalty structures for NFTs and collections according to
    EIP-24 standard.
    """
    
    def __init__(self):
        """Initialize RoyaltyManager."""
        self.logger = logging.getLogger(__name__)
    
    def create_royalty_structure(
        self,
        recipients: List[Dict[str, Any]],
        validate: bool = True
    ) -> Dict[str, Any]:
        """
        Create a royalty structure with multiple recipients.
        
        Args:
            recipients: List of royalty recipients with addresses and percentages
            validate: Whether to validate the structure
            
        Returns:
            EIP-24 compliant royalty structure
            
        Example:
            >>> royalties = manager.create_royalty_structure([
            ...     {"address": "9fArtist...", "percentage": 80, "name": "Artist"},
            ...     {"address": "9fCharity...", "percentage": 15, "name": "Charity"},
            ...     {"address": "9fPlatform...", "percentage": 5, "name": "Platform"}
            ... ])
        """
        self.logger.info(f"Creating royalty structure with {len(recipients)} recipients")
        
        if validate:
            self._validate_royalty_structure(recipients)
        
        # Calculate total percentage
        total_percentage = sum(r.get('percentage', 0) for r in recipients)
        
        # Create EIP-24 compliant structure
        royalty_structure = {
            'recipients': [
                {
                    'address': r['address'],
                    'percentage': r['percentage'],
                    'name': r.get('name', f'Recipient {i+1}'),
                    'description': r.get('description', '')
                }
                for i, r in enumerate(recipients)
            ],
            'total_percentage': total_percentage,
            'recipient_count': len(recipients),
            'standard': 'EIP-24'
        }
        
        self.logger.info(f"Royalty structure created: {total_percentage}% total across {len(recipients)} recipients")
        return royalty_structure
    
    def create_artist_charity_platform_split(
        self,
        artist_address: str,
        artist_percentage: float = 80.0,
        charity_address: Optional[str] = None,
        charity_percentage: float = 15.0,
        platform_address: Optional[str] = None,
        platform_percentage: float = 5.0
    ) -> Dict[str, Any]:
        """
        Create a common 3-way royalty split between artist, charity, and platform.
        
        Args:
            artist_address: Artist's address
            artist_percentage: Artist's royalty percentage
            charity_address: Charity address (optional)
            charity_percentage: Charity royalty percentage
            platform_address: Platform address (optional)
            platform_percentage: Platform royalty percentage
            
        Returns:
            Royalty structure
        """
        recipients = [
            {
                'address': artist_address,
                'percentage': artist_percentage,
                'name': 'Artist',
                'description': 'Original creator of the artwork'
            }
        ]
        
        if charity_address:
            recipients.append({
                'address': charity_address,
                'percentage': charity_percentage,
                'name': 'Charity',
                'description': 'Charitable organization'
            })
        
        if platform_address:
            recipients.append({
                'address': platform_address,
                'percentage': platform_percentage,
                'name': 'Platform',
                'description': 'Platform or marketplace'
            })
        
        return self.create_royalty_structure(recipients)
    
    def create_collaborative_split(
        self,
        collaborators: List[Dict[str, Any]],
        equal_split: bool = False
    ) -> Dict[str, Any]:
        """
        Create royalty structure for collaborative works.
        
        Args:
            collaborators: List of collaborators with addresses and optional percentages
            equal_split: If True, split equally among all collaborators
            
        Returns:
            Royalty structure
            
        Example:
            >>> royalties = manager.create_collaborative_split([
            ...     {"address": "9fArtist1...", "name": "Artist 1", "role": "Designer"},
            ...     {"address": "9fArtist2...", "name": "Artist 2", "role": "Animator"},
            ...     {"address": "9fMusician...", "name": "Musician", "role": "Music"}
            ... ], equal_split=True)
        """
        if equal_split:
            # Calculate equal percentage for each collaborator
            equal_percentage = 100.0 / len(collaborators)
            for collaborator in collaborators:
                collaborator['percentage'] = equal_percentage
        
        # Add default descriptions based on roles
        for i, collaborator in enumerate(collaborators):
            if 'description' not in collaborator:
                role = collaborator.get('role', f'Collaborator {i+1}')
                collaborator['description'] = f'Collaborative work contributor - {role}'
        
        return self.create_royalty_structure(collaborators)
    
    def validate_royalty_structure(self, royalty_structure: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a royalty structure and return validation result.
        
        Args:
            royalty_structure: Royalty structure to validate
            
        Returns:
            Validation result with errors and warnings
        """
        errors = []
        warnings = []
        
        recipients = royalty_structure.get('recipients', [])
        
        if not recipients:
            errors.append("No royalty recipients specified")
            return {"valid": False, "errors": errors, "warnings": warnings}
        
        # Validate each recipient
        total_percentage = 0
        for i, recipient in enumerate(recipients):
            # Check required fields
            if 'address' not in recipient:
                errors.append(f"Recipient {i+1} missing address")
            
            if 'percentage' not in recipient:
                errors.append(f"Recipient {i+1} missing percentage")
            else:
                percentage = recipient['percentage']
                if not isinstance(percentage, (int, float)):
                    errors.append(f"Recipient {i+1} percentage must be a number")
                elif percentage < 0:
                    errors.append(f"Recipient {i+1} percentage cannot be negative")
                elif percentage > 100:
                    errors.append(f"Recipient {i+1} percentage cannot exceed 100%")
                else:
                    total_percentage += percentage
        
        # Check total percentage
        if total_percentage > 100:
            errors.append(f"Total royalty percentage ({total_percentage}%) exceeds 100%")
        elif total_percentage > 50:
            warnings.append(f"High total royalty percentage: {total_percentage}%")
        elif total_percentage == 0:
            warnings.append("No royalties specified (0% total)")
        
        # Check for duplicate addresses
        addresses = [r.get('address') for r in recipients if 'address' in r]
        if len(addresses) != len(set(addresses)):
            warnings.append("Duplicate addresses found in royalty recipients")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "total_percentage": total_percentage,
            "recipient_count": len(recipients)
        }
    
    def calculate_royalty_distribution(
        self,
        royalty_structure: Dict[str, Any],
        sale_amount_erg: float
    ) -> Dict[str, Any]:
        """
        Calculate royalty distribution for a given sale amount.
        
        Args:
            royalty_structure: Royalty structure
            sale_amount_erg: Sale amount in ERG
            
        Returns:
            Distribution breakdown with amounts for each recipient
        """
        recipients = royalty_structure.get('recipients', [])
        
        if not recipients:
            return {
                "total_royalties_erg": 0,
                "distributions": [],
                "remaining_to_seller_erg": sale_amount_erg
            }
        
        distributions = []
        total_royalties = 0
        
        for recipient in recipients:
            percentage = recipient.get('percentage', 0)
            royalty_amount = (sale_amount_erg * percentage) / 100
            total_royalties += royalty_amount
            
            distributions.append({
                "address": recipient['address'],
                "name": recipient.get('name', 'Unknown'),
                "percentage": percentage,
                "amount_erg": royalty_amount,
                "amount_nanoerg": AmountUtils.erg_to_nanoerg(royalty_amount)
            })
        
        remaining_to_seller = sale_amount_erg - total_royalties
        
        return {
            "sale_amount_erg": sale_amount_erg,
            "total_royalties_erg": total_royalties,
            "total_royalty_percentage": sum(r.get('percentage', 0) for r in recipients),
            "distributions": distributions,
            "remaining_to_seller_erg": remaining_to_seller,
            "recipient_count": len(distributions)
        }
    
    def encode_royalties_for_register(self, royalty_structure: Dict[str, Any]) -> Dict[str, Any]:
        """
        Encode royalty structure for EIP-24 R5 register.
        
        Args:
            royalty_structure: Royalty structure to encode
            
        Returns:
            EIP-24 compliant register data
        """
        recipients = royalty_structure.get('recipients', [])
        
        encoded = {
            'recipients': [
                {
                    'address': r['address'],
                    'percentage': r['percentage']
                }
                for r in recipients
            ],
            'total_percentage': sum(r.get('percentage', 0) for r in recipients),
            'standard': 'EIP-24'
        }
        
        return encoded
    
    def create_tiered_royalty_structure(
        self,
        primary_recipients: List[Dict[str, Any]],
        secondary_recipients: Optional[List[Dict[str, Any]]] = None,
        primary_percentage: float = 80.0
    ) -> Dict[str, Any]:
        """
        Create a tiered royalty structure with primary and secondary recipients.
        
        Args:
            primary_recipients: Primary royalty recipients (e.g., creators)
            secondary_recipients: Secondary recipients (e.g., platform, charity)
            primary_percentage: Total percentage allocated to primary recipients
            
        Returns:
            Tiered royalty structure
        """
        if not primary_recipients:
            raise ValueError("At least one primary recipient is required")
        
        # Calculate percentages for primary recipients
        primary_individual_percentage = primary_percentage / len(primary_recipients)
        
        all_recipients = []
        
        # Add primary recipients
        for i, recipient in enumerate(primary_recipients):
            all_recipients.append({
                'address': recipient['address'],
                'percentage': primary_individual_percentage,
                'name': recipient.get('name', f'Primary Creator {i+1}'),
                'description': recipient.get('description', 'Primary creator'),
                'tier': 'primary'
            })
        
        # Add secondary recipients
        if secondary_recipients:
            secondary_percentage = 100.0 - primary_percentage
            secondary_individual_percentage = secondary_percentage / len(secondary_recipients)
            
            for i, recipient in enumerate(secondary_recipients):
                all_recipients.append({
                    'address': recipient['address'],
                    'percentage': secondary_individual_percentage,
                    'name': recipient.get('name', f'Secondary Recipient {i+1}'),
                    'description': recipient.get('description', 'Secondary recipient'),
                    'tier': 'secondary'
                })
        
        return self.create_royalty_structure(all_recipients)
    
    def _validate_royalty_structure(self, recipients: List[Dict[str, Any]]):
        """Validate royalty structure and raise errors if invalid."""
        if not recipients:
            raise ValueError("At least one royalty recipient is required")
        
        total_percentage = 0
        addresses = []
        
        for i, recipient in enumerate(recipients):
            # Check required fields
            if 'address' not in recipient:
                raise ValueError(f"Recipient {i+1} missing required field 'address'")
            if 'percentage' not in recipient:
                raise ValueError(f"Recipient {i+1} missing required field 'percentage'")
            
            address = recipient['address']
            percentage = recipient['percentage']
            
            # Validate address format (basic check)
            if not isinstance(address, str) or len(address) < 10:
                raise ValueError(f"Recipient {i+1} invalid address format: {address}")
            
            # Validate percentage
            if not isinstance(percentage, (int, float)):
                raise ValueError(f"Recipient {i+1} percentage must be a number, got {type(percentage)}")
            if percentage < 0:
                raise ValueError(f"Recipient {i+1} percentage cannot be negative: {percentage}")
            if percentage > 100:
                raise ValueError(f"Recipient {i+1} percentage cannot exceed 100%: {percentage}")
            
            total_percentage += percentage
            addresses.append(address)
        
        # Check total percentage
        if total_percentage > 100:
            raise ValueError(f"Total royalty percentage ({total_percentage}%) exceeds 100%")
        
        # Check for duplicate addresses
        if len(addresses) != len(set(addresses)):
            raise ValueError("Duplicate addresses found in royalty recipients")
    
    def get_royalty_summary(self, royalty_structure: Dict[str, Any]) -> str:
        """
        Get a human-readable summary of the royalty structure.
        
        Args:
            royalty_structure: Royalty structure
            
        Returns:
            Summary string
        """
        recipients = royalty_structure.get('recipients', [])
        total_percentage = sum(r.get('percentage', 0) for r in recipients)
        
        summary_lines = [
            f"Royalty Structure Summary:",
            f"  Recipients: {len(recipients)}",
            f"  Total Percentage: {total_percentage}%",
            ""
        ]
        
        for i, recipient in enumerate(recipients):
            name = recipient.get('name', f'Recipient {i+1}')
            percentage = recipient.get('percentage', 0)
            address = recipient.get('address', 'Unknown')
            
            summary_lines.append(f"  {i+1}. {name}: {percentage}% ({address[:10]}...)")
        
        return "\n".join(summary_lines)
    
    def __str__(self) -> str:
        """String representation of RoyaltyManager."""
        return "RoyaltyManager()"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return "RoyaltyManager(standard='EIP-24')"