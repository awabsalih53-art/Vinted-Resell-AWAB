"""
Supabase Database Layer for Awab Reselling Dashboard
Replaces the old SQLite db.py with Supabase connections
"""

import os
from supabase import create_client, Client
from typing import Optional, List, Dict, Any
from datetime import datetime
from logger import get_logger

logger = get_logger(__name__)

# Supabase connection
_supabase_client: Optional[Client] = None


def get_supabase() -> Client:
    """Get or create Supabase client"""
    global _supabase_client

    if _supabase_client is None:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_ANON_KEY")

        if not url or not key:
            raise Exception("SUPABASE_URL and SUPABASE_ANON_KEY environment variables required")

        _supabase_client = create_client(url, key)
        logger.info("Supabase client initialized")

    return _supabase_client


# ============================================================================
# SETTINGS
# ============================================================================

def get_setting(key: str) -> Optional[str]:
    """Get a setting value by key"""
    try:
        supabase = get_supabase()
        result = supabase.table('settings').select('value').eq('key', key).maybeSingle().execute()
        return result.data['value'] if result.data else None
    except Exception as e:
        logger.error(f"Error getting setting {key}: {e}")
        return None


def set_setting(key: str, value: str, description: str = None) -> bool:
    """Set a setting value"""
    try:
        supabase = get_supabase()
        data = {'key': key, 'value': value, 'updated_at': datetime.utcnow().isoformat()}
        if description:
            data['description'] = description

        supabase.table('settings').upsert(data).execute()
        return True
    except Exception as e:
        logger.error(f"Error setting {key}: {e}")
        return False


def get_all_settings() -> Dict[str, str]:
    """Get all settings as a dictionary"""
    try:
        supabase = get_supabase()
        result = supabase.table('settings').select('key, value').execute()
        return {row['key']: row['value'] for row in result.data}
    except Exception as e:
        logger.error(f"Error getting all settings: {e}")
        return {}


# ============================================================================
# ITEMS (INVENTORY)
# ============================================================================

def get_items(limit: int = 50, filters: Dict[str, Any] = None) -> List[Dict]:
    """Get items with optional filters"""
    try:
        supabase = get_supabase()
        query = supabase.table('items').select('*')

        if filters:
            if 'listing_status' in filters:
                query = query.eq('listing_status', filters['listing_status'])
            if 'category' in filters:
                query = query.eq('category', filters['category'])
            if 'brand' in filters:
                query = query.ilike('brand', f"%{filters['brand']}%")

        query = query.order('created_at', desc=True).limit(limit)
        result = query.execute()
        return result.data
    except Exception as e:
        logger.error(f"Error getting items: {e}")
        return []


def get_item_by_id(item_id: str) -> Optional[Dict]:
    """Get a single item by ID"""
    try:
        supabase = get_supabase()
        result = supabase.table('items').select('*').eq('id', item_id).maybeSingle().execute()
        return result.data
    except Exception as e:
        logger.error(f"Error getting item {item_id}: {e}")
        return None


def get_item_by_sku(sku: str) -> Optional[Dict]:
    """Get a single item by SKU"""
    try:
        supabase = get_supabase()
        result = supabase.table('items').select('*').eq('sku', sku).maybeSingle().execute()
        return result.data
    except Exception as e:
        logger.error(f"Error getting item by SKU {sku}: {e}")
        return None


def get_item_by_vinted_id(vinted_item_id: str) -> Optional[Dict]:
    """Get item by Vinted item ID (for integration)"""
    try:
        supabase = get_supabase()
        result = supabase.table('items').select('*').eq('vinted_item_id', vinted_item_id).maybeSingle().execute()
        return result.data
    except Exception as e:
        logger.error(f"Error getting item by Vinted ID {vinted_item_id}: {e}")
        return None


def create_item(item_data: Dict) -> Optional[Dict]:
    """Create a new item"""
    try:
        supabase = get_supabase()
        result = supabase.table('items').insert(item_data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Error creating item: {e}")
        return None


def update_item(item_id: str, item_data: Dict) -> bool:
    """Update an item"""
    try:
        supabase = get_supabase()
        item_data['updated_at'] = datetime.utcnow().isoformat()
        supabase.table('items').update(item_data).eq('id', item_id).execute()
        return True
    except Exception as e:
        logger.error(f"Error updating item {item_id}: {e}")
        return False


def delete_item(item_id: str) -> bool:
    """Delete an item"""
    try:
        supabase = get_supabase()
        supabase.table('items').delete().eq('id', item_id).execute()
        return True
    except Exception as e:
        logger.error(f"Error deleting item {item_id}: {e}")
        return False


def get_items_stats() -> Dict:
    """Get inventory statistics"""
    try:
        supabase = get_supabase()

        # Total items
        all_items = supabase.table('items').select('listing_status, profit').execute()
        total = len(all_items.data)

        # Count by status
        listed = sum(1 for item in all_items.data if item['listing_status'] == 'Listed')
        sold = sum(1 for item in all_items.data if item['listing_status'] == 'Sold')
        draft = sum(1 for item in all_items.data if item['listing_status'] == 'Draft')

        # Total profit (from sold items)
        total_profit = sum(float(item['profit'] or 0) for item in all_items.data if item['listing_status'] == 'Sold')

        return {
            'total_items': total,
            'listed': listed,
            'sold': sold,
            'draft': draft,
            'total_profit': round(total_profit, 2)
        }
    except Exception as e:
        logger.error(f"Error getting items stats: {e}")
        return {'total_items': 0, 'listed': 0, 'sold': 0, 'draft': 0, 'total_profit': 0}


# ============================================================================
# SALES
# ============================================================================

def get_sales(limit: int = 50, filters: Dict[str, Any] = None) -> List[Dict]:
    """Get sales with optional filters"""
    try:
        supabase = get_supabase()
        query = supabase.table('sales').select('*')

        if filters:
            if 'platform' in filters:
                query = query.eq('platform', filters['platform'])
            if 'payout_status' in filters:
                query = query.eq('payout_status', filters['payout_status'])

        query = query.order('date_sold', desc=True).limit(limit)
        result = query.execute()
        return result.data
    except Exception as e:
        logger.error(f"Error getting sales: {e}")
        return []


def get_sale_by_id(sale_id: str) -> Optional[Dict]:
    """Get a single sale by ID"""
    try:
        supabase = get_supabase()
        result = supabase.table('sales').select('*').eq('id', sale_id).maybeSingle().execute()
        return result.data
    except Exception as e:
        logger.error(f"Error getting sale {sale_id}: {e}")
        return None


def create_sale(sale_data: Dict) -> Optional[Dict]:
    """Create a new sale"""
    try:
        supabase = get_supabase()
        result = supabase.table('sales').insert(sale_data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Error creating sale: {e}")
        return None


def update_sale(sale_id: str, sale_data: Dict) -> bool:
    """Update a sale"""
    try:
        supabase = get_supabase()
        sale_data['updated_at'] = datetime.utcnow().isoformat()
        supabase.table('sales').update(sale_data).eq('id', sale_id).execute()
        return True
    except Exception as e:
        logger.error(f"Error updating sale {sale_id}: {e}")
        return False


def get_sales_stats() -> Dict:
    """Get sales statistics"""
    try:
        supabase = get_supabase()
        result = supabase.table('sales').select('net_profit, sale_price, platform').execute()

        total_sales = len(result.data)
        total_revenue = sum(float(sale['sale_price'] or 0) for sale in result.data)
        total_profit = sum(float(sale['net_profit'] or 0) for sale in result.data)

        # Average profit
        avg_profit = total_profit / total_sales if total_sales > 0 else 0

        return {
            'total_sales': total_sales,
            'total_revenue': round(total_revenue, 2),
            'total_profit': round(total_profit, 2),
            'avg_profit': round(avg_profit, 2)
        }
    except Exception as e:
        logger.error(f"Error getting sales stats: {e}")
        return {'total_sales': 0, 'total_revenue': 0, 'total_profit': 0, 'avg_profit': 0}


# ============================================================================
# SHIPMENTS
# ============================================================================

def get_shipments(status_filter: str = None, limit: int = 50) -> List[Dict]:
    """Get shipments, optionally filtered by status"""
    try:
        supabase = get_supabase()
        query = supabase.table('shipments').select('*')

        if status_filter:
            query = query.eq('status', status_filter)

        query = query.order('created_at', desc=True).limit(limit)
        result = query.execute()
        return result.data
    except Exception as e:
        logger.error(f"Error getting shipments: {e}")
        return []


def create_shipment(shipment_data: Dict) -> Optional[Dict]:
    """Create a new shipment"""
    try:
        supabase = get_supabase()
        result = supabase.table('shipments').insert(shipment_data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Error creating shipment: {e}")
        return None


def update_shipment(shipment_id: str, shipment_data: Dict) -> bool:
    """Update a shipment"""
    try:
        supabase = get_supabase()
        shipment_data['updated_at'] = datetime.utcnow().isoformat()
        supabase.table('shipments').update(shipment_data).eq('id', shipment_id).execute()
        return True
    except Exception as e:
        logger.error(f"Error updating shipment {shipment_id}: {e}")
        return False


# ============================================================================
# RETURN CASES
# ============================================================================

def get_return_cases(status_filter: str = None, limit: int = 50) -> List[Dict]:
    """Get return cases, optionally filtered by status"""
    try:
        supabase = get_supabase()
        query = supabase.table('return_cases').select('*')

        if status_filter:
            query = query.eq('status', status_filter)

        query = query.order('created_at', desc=True).limit(limit)
        result = query.execute()
        return result.data
    except Exception as e:
        logger.error(f"Error getting return cases: {e}")
        return []


def create_return_case(return_data: Dict) -> Optional[Dict]:
    """Create a new return case"""
    try:
        supabase = get_supabase()
        result = supabase.table('return_cases').insert(return_data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Error creating return case: {e}")
        return None


def update_return_case(return_id: str, return_data: Dict) -> bool:
    """Update a return case"""
    try:
        supabase = get_supabase()
        return_data['updated_at'] = datetime.utcnow().isoformat()
        supabase.table('return_cases').update(return_data).eq('id', return_id).execute()
        return True
    except Exception as e:
        logger.error(f"Error updating return case {return_id}: {e}")
        return False


# ============================================================================
# TASKS
# ============================================================================

def get_tasks(status_filter: str = None, limit: int = 50) -> List[Dict]:
    """Get tasks, optionally filtered by status"""
    try:
        supabase = get_supabase()
        query = supabase.table('tasks').select('*')

        if status_filter:
            query = query.eq('status', status_filter)

        query = query.order('created_at', desc=True).limit(limit)
        result = query.execute()
        return result.data
    except Exception as e:
        logger.error(f"Error getting tasks: {e}")
        return []


def create_task(task_data: Dict) -> Optional[Dict]:
    """Create a new task"""
    try:
        supabase = get_supabase()
        result = supabase.table('tasks').insert(task_data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        return None


def update_task(task_id: str, task_data: Dict) -> bool:
    """Update a task"""
    try:
        supabase = get_supabase()
        task_data['updated_at'] = datetime.utcnow().isoformat()
        supabase.table('tasks').update(task_data).eq('id', task_id).execute()
        return True
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {e}")
        return False


def delete_task(task_id: str) -> bool:
    """Delete a task"""
    try:
        supabase = get_supabase()
        supabase.table('tasks').delete().eq('id', task_id).execute()
        return True
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {e}")
        return False


# ============================================================================
# VINTED INTEGRATION LOGS
# ============================================================================

def log_vinted_event(event_type: str, status: str, message: str, data: Dict = None) -> bool:
    """Log a Vinted integration event"""
    try:
        supabase = get_supabase()
        log_data = {
            'event_type': event_type,
            'status': status,
            'message': message,
            'data': data
        }
        supabase.table('vinted_integration_logs').insert(log_data).execute()
        return True
    except Exception as e:
        logger.error(f"Error logging Vinted event: {e}")
        return False


def get_vinted_logs(limit: int = 100) -> List[Dict]:
    """Get recent Vinted integration logs"""
    try:
        supabase = get_supabase()
        result = supabase.table('vinted_integration_logs').select('*').order('created_at', desc=True).limit(limit).execute()
        return result.data
    except Exception as e:
        logger.error(f"Error getting Vinted logs: {e}")
        return []
