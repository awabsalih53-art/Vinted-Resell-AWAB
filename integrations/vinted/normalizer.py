"""
Vinted Normalizer

Converts Vinted API data structures into internal dashboard models.
This creates a clean separation between the Vinted API and our app.
"""

from datetime import datetime
from typing import Dict, Optional, Any
from logger import get_logger
import uuid

logger = get_logger(__name__)


class VintedNormalizer:
    """Normalizes Vinted data into internal Item/Sale models"""

    @staticmethod
    def generate_sku(vinted_item_id: str, brand: str = None) -> str:
        """Generate a SKU for a Vinted item"""
        prefix = "VINT"
        if brand:
            # Use first 3 letters of brand, uppercase
            brand_code = brand[:3].upper().replace(" ", "")
            prefix = f"VINT-{brand_code}"
        return f"{prefix}-{vinted_item_id}"

    @staticmethod
    def normalize_item(vinted_item: Any, query_id: int = None) -> Dict:
        """
        Convert a pyVintedVN Item object to our internal Item format

        Args:
            vinted_item: Item object from pyVintedVN
            query_id: ID of the Vinted query that found this item

        Returns:
            Dictionary ready for database.create_item()
        """
        try:
            # Extract data from the Vinted item
            sku = VintedNormalizer.generate_sku(str(vinted_item.id), vinted_item.brand_title)

            # Map condition if available (Vinted doesn't always provide this in the item object)
            # Default to "Good" for sourced items
            condition = "Good"

            # Estimate fees (Vinted charges ~10%)
            price = float(vinted_item.price)
            fees_estimate = round(price * 0.10, 2)

            # Create the normalized item
            item_data = {
                'sku': sku,
                'item_name': vinted_item.title,
                'category': None,  # Vinted doesn't expose category in simple search
                'size': vinted_item.size_title if hasattr(vinted_item, 'size_title') and vinted_item.size_title else None,
                'condition': condition,
                'brand': vinted_item.brand_title if vinted_item.brand_title else "Unknown",
                'platforms': ['Vinted'],
                'listing_status': 'Draft',  # Items from Vinted start as drafts in our inventory
                'purchase_price': None,  # User needs to enter this
                'fees_estimate': fees_estimate,
                'shipping_paid_by': 'Buyer',  # Vinted default
                'shipping_cost': 0,  # Buyer pays on Vinted
                'sale_price': price,  # List price from Vinted
                'date_purchased': None,
                'date_listed': vinted_item.created_at_ts.isoformat() if hasattr(vinted_item, 'created_at_ts') else None,
                'date_sold': None,
                'location': None,
                'notes': f"Imported from Vinted. Original URL: {vinted_item.url}",
                'photos': [vinted_item.photo] if vinted_item.photo else [],
                'vinted_item_id': str(vinted_item.id),
                'vinted_query_id': query_id
            }

            return item_data

        except Exception as e:
            logger.error(f"Error normalizing Vinted item: {e}", exc_info=True)
            return None

    @staticmethod
    def normalize_user_country(profile_id: str, country_code: str) -> Dict:
        """
        Normalize Vinted user country data

        Args:
            profile_id: Vinted user profile ID
            country_code: 2-letter ISO country code

        Returns:
            Dictionary with normalized country info
        """
        return {
            'profile_id': profile_id,
            'country_code': country_code.upper() if country_code else "XX"
        }

    @staticmethod
    def can_import_item(vinted_item: Any, allowlist: list = None, banwords: list = None) -> tuple[bool, Optional[str]]:
        """
        Check if a Vinted item should be imported

        Args:
            vinted_item: Item from pyVintedVN
            allowlist: List of allowed country codes (or None for all)
            banwords: List of banned words in titles

        Returns:
            Tuple of (should_import: bool, reason: Optional[str])
        """
        # Check banwords
        if banwords:
            title_lower = vinted_item.title.lower()
            for word in banwords:
                if word.lower() in title_lower:
                    return False, f"Title contains banword: {word}"

        # Allowlist check would require fetching user country
        # We'll handle that in the adapter layer

        return True, None
