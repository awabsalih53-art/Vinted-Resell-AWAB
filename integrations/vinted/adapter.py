"""
Vinted Adapter

High-level interface for Vinted integration.
Handles syncing Vinted items into the dashboard inventory.
"""

import sys
import os
from typing import List, Dict, Optional
from datetime import datetime

# Add parent directories to path to import existing modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pyVintedVN import Vinted
from integrations.vinted.normalizer import VintedNormalizer
import database as db
from logger import get_logger

logger = get_logger(__name__)


class VintedAdapter:
    """
    Adapter for Vinted integration.
    Provides safe, monitored access to Vinted data.
    """

    def __init__(self):
        self.vinted_client = Vinted()
        self.normalizer = VintedNormalizer()
        self.enabled = self._check_enabled()

    def _check_enabled(self) -> bool:
        """Check if Vinted integration is enabled"""
        try:
            enabled = db.get_setting('vinted_integration_enabled')
            return enabled == 'true'
        except Exception as e:
            logger.error(f"Error checking Vinted integration status: {e}")
            return False

    def is_enabled(self) -> bool:
        """Public method to check if integration is enabled"""
        return self.enabled

    def get_status(self) -> Dict:
        """
        Get integration status info

        Returns:
            Dict with status information
        """
        last_sync = db.get_setting('vinted_last_sync')
        last_sync_time = None

        if last_sync and last_sync != '0':
            try:
                last_sync_time = datetime.fromtimestamp(float(last_sync)).isoformat()
            except:
                pass

        return {
            'enabled': self.enabled,
            'last_sync': last_sync_time,
            'sync_interval': db.get_setting('vinted_sync_interval') or '60'
        }

    def sync_query(self, query_url: str, query_id: int, items_limit: int = 20) -> Dict:
        """
        Sync items from a Vinted search query

        Args:
            query_url: Vinted search URL
            query_id: Internal query ID
            items_limit: Maximum items to fetch

        Returns:
            Dict with sync results: {success: bool, imported: int, skipped: int, errors: int}
        """
        if not self.enabled:
            logger.warning("Vinted integration is disabled")
            return {'success': False, 'imported': 0, 'skipped': 0, 'errors': 0, 'message': 'Integration disabled'}

        result = {'success': True, 'imported': 0, 'skipped': 0, 'errors': 0, 'items': []}

        try:
            # Fetch items from Vinted
            logger.info(f"Fetching Vinted items for query {query_id}")
            vinted_items = self.vinted_client.items.search(query_url, nbr_items=items_limit)

            # Get banwords from settings
            banwords_str = db.get_setting('banwords') or ''
            banwords = [w.strip().lower() for w in banwords_str.split('|||') if w.strip()]

            for vinted_item in vinted_items:
                try:
                    # Check if we should import this item
                    should_import, reason = self.normalizer.can_import_item(vinted_item, banwords=banwords)

                    if not should_import:
                        result['skipped'] += 1
                        logger.debug(f"Skipped Vinted item {vinted_item.id}: {reason}")
                        continue

                    # Check if item already exists
                    existing = db.get_item_by_vinted_id(str(vinted_item.id))
                    if existing:
                        result['skipped'] += 1
                        logger.debug(f"Item {vinted_item.id} already in database")
                        continue

                    # Normalize the Vinted item to our format
                    normalized_item = self.normalizer.normalize_item(vinted_item, query_id)

                    if not normalized_item:
                        result['errors'] += 1
                        logger.error(f"Failed to normalize Vinted item {vinted_item.id}")
                        continue

                    # Create item in database
                    created_item = db.create_item(normalized_item)

                    if created_item:
                        result['imported'] += 1
                        result['items'].append(created_item)
                        logger.info(f"Imported Vinted item {vinted_item.id} as {created_item['sku']}")

                        # Log the event
                        db.log_vinted_event(
                            event_type='item_imported',
                            status='Success',
                            message=f"Imported item {vinted_item.title}",
                            data={'vinted_id': str(vinted_item.id), 'sku': created_item['sku']}
                        )
                    else:
                        result['errors'] += 1
                        logger.error(f"Failed to create item in database for Vinted item {vinted_item.id}")

                except Exception as e:
                    result['errors'] += 1
                    logger.error(f"Error processing Vinted item: {e}", exc_info=True)

            # Update last sync time
            db.set_setting('vinted_last_sync', str(int(datetime.now().timestamp())))

            # Log the sync event
            db.log_vinted_event(
                event_type='query_sync',
                status='Success',
                message=f"Synced query {query_id}: {result['imported']} imported, {result['skipped']} skipped, {result['errors']} errors",
                data={'query_id': query_id, 'results': result}
            )

        except Exception as e:
            result['success'] = False
            result['message'] = str(e)
            logger.error(f"Error syncing Vinted query {query_id}: {e}", exc_info=True)

            # Log the error
            db.log_vinted_event(
                event_type='query_sync',
                status='Error',
                message=f"Failed to sync query {query_id}: {str(e)}",
                data={'query_id': query_id, 'error': str(e)}
            )

        return result

    def enable_integration(self) -> bool:
        """Enable Vinted integration"""
        try:
            db.set_setting('vinted_integration_enabled', 'true')
            self.enabled = True
            logger.info("Vinted integration enabled")

            db.log_vinted_event(
                event_type='integration_enabled',
                status='Success',
                message="Vinted integration enabled"
            )
            return True
        except Exception as e:
            logger.error(f"Error enabling Vinted integration: {e}")
            return False

    def disable_integration(self) -> bool:
        """Disable Vinted integration"""
        try:
            db.set_setting('vinted_integration_enabled', 'false')
            self.enabled = False
            logger.info("Vinted integration disabled")

            db.log_vinted_event(
                event_type='integration_disabled',
                status='Success',
                message="Vinted integration disabled"
            )
            return True
        except Exception as e:
            logger.error(f"Error disabling Vinted integration: {e}")
            return False

    def test_connection(self) -> Dict:
        """
        Test Vinted API connection

        Returns:
            Dict with test results
        """
        try:
            # Try a simple search
            test_url = "https://www.vinted.co.uk/catalog?search_text=nike"
            items = self.vinted_client.items.search(test_url, nbr_items=1)

            if items:
                db.log_vinted_event(
                    event_type='connection_test',
                    status='Success',
                    message="Vinted API connection successful"
                )
                return {'success': True, 'message': 'Connection successful'}
            else:
                db.log_vinted_event(
                    event_type='connection_test',
                    status='Warning',
                    message="Vinted API returned no items"
                )
                return {'success': True, 'message': 'Connected but no items returned'}

        except Exception as e:
            logger.error(f"Vinted connection test failed: {e}", exc_info=True)

            db.log_vinted_event(
                event_type='connection_test',
                status='Error',
                message=f"Connection test failed: {str(e)}",
                data={'error': str(e)}
            )

            return {'success': False, 'message': str(e)}
