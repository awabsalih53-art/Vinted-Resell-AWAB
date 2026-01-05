"""
Seed Data Script for Awab Reselling Dashboard
Populates the database with demo data for testing
"""

import database as db
from datetime import datetime, timedelta
import random
from logger import get_logger

logger = get_logger(__name__)


def seed_demo_data():
    """Populate database with demo inventory, sales, and other data"""

    logger.info("Starting database seed...")

    # Demo items data
    demo_items = [
        {
            'sku': 'VINT-NIK-001',
            'item_name': 'Nike Air Max 90 White',
            'category': 'Trainers',
            'size': 'UK 10',
            'condition': 'Like New',
            'brand': 'Nike',
            'platforms': ['Vinted'],
            'listing_status': 'Sold',
            'purchase_price': 45.00,
            'fees_estimate': 8.50,
            'shipping_paid_by': 'Buyer',
            'shipping_cost': 0,
            'sale_price': 85.00,
            'date_purchased': (datetime.now() - timedelta(days=30)).isoformat(),
            'date_listed': (datetime.now() - timedelta(days=25)).isoformat(),
            'date_sold': (datetime.now() - timedelta(days=5)).isoformat(),
            'location': 'Warehouse',
            'notes': 'Great condition, sold quickly'
        },
        {
            'sku': 'VINT-ADI-002',
            'item_name': 'Adidas Ultraboost 21 Black',
            'category': 'Trainers',
            'size': 'UK 9',
            'condition': 'Good',
            'brand': 'Adidas',
            'platforms': ['Vinted', 'Depop'],
            'listing_status': 'Listed',
            'purchase_price': 35.00,
            'fees_estimate': 6.50,
            'shipping_paid_by': 'Buyer',
            'shipping_cost': 0,
            'sale_price': 65.00,
            'date_purchased': (datetime.now() - timedelta(days=20)).isoformat(),
            'date_listed': (datetime.now() - timedelta(days=15)).isoformat(),
            'location': 'Home',
            'notes': 'Listed on multiple platforms'
        },
        {
            'sku': 'VINT-LEV-003',
            'item_name': 'Levis 501 Vintage Jeans',
            'category': 'Jeans',
            'size': 'W32 L32',
            'condition': 'New',
            'brand': 'Levis',
            'platforms': ['Vinted'],
            'listing_status': 'Listed',
            'purchase_price': 25.00,
            'fees_estimate': 4.00,
            'shipping_paid_by': 'Buyer',
            'shipping_cost': 0,
            'sale_price': 40.00,
            'date_purchased': (datetime.now() - timedelta(days=10)).isoformat(),
            'date_listed': (datetime.now() - timedelta(days=5)).isoformat(),
            'location': 'Warehouse',
            'notes': 'Brand new with tags'
        },
        {
            'sku': 'VINT-NOR-004',
            'item_name': 'The North Face Jacket Green',
            'category': 'Outerwear',
            'size': 'L',
            'condition': 'Like New',
            'brand': 'The North Face',
            'platforms': ['Vinted'],
            'listing_status': 'Sold',
            'purchase_price': 60.00,
            'fees_estimate': 12.00,
            'shipping_paid_by': 'Buyer',
            'shipping_cost': 0,
            'sale_price': 120.00,
            'date_purchased': (datetime.now() - timedelta(days=40)).isoformat(),
            'date_listed': (datetime.now() - timedelta(days=35)).isoformat(),
            'date_sold': (datetime.now() - timedelta(days=10)).isoformat(),
            'location': 'Warehouse',
            'notes': 'Premium item, high profit margin'
        },
        {
            'sku': 'VINT-PAT-005',
            'item_name': 'Patagonia Fleece Navy',
            'category': 'Fleece',
            'size': 'M',
            'condition': 'Good',
            'brand': 'Patagonia',
            'platforms': ['Depop'],
            'listing_status': 'Draft',
            'purchase_price': 30.00,
            'fees_estimate': 5.50,
            'shipping_paid_by': 'Buyer',
            'shipping_cost': 0,
            'sale_price': 55.00,
            'date_purchased': (datetime.now() - timedelta(days=3)).isoformat(),
            'location': 'Home',
            'notes': 'Needs photos before listing'
        },
        {
            'sku': 'VINT-PUM-006',
            'item_name': 'Puma Suede Classic Red',
            'category': 'Trainers',
            'size': 'UK 8',
            'condition': 'Good',
            'brand': 'Puma',
            'platforms': ['Vinted'],
            'listing_status': 'Listed',
            'purchase_price': 20.00,
            'fees_estimate': 3.50,
            'shipping_paid_by': 'Buyer',
            'shipping_cost': 0,
            'sale_price': 35.00,
            'date_purchased': (datetime.now() - timedelta(days=7)).isoformat(),
            'date_listed': (datetime.now() - timedelta(days=2)).isoformat(),
            'location': 'Warehouse',
            'notes': 'Classic style, should sell fast'
        }
    ]

    # Create items
    created_items = []
    for item_data in demo_items:
        try:
            item = db.create_item(item_data)
            if item:
                created_items.append(item)
                logger.info(f"Created item: {item['sku']}")
        except Exception as e:
            logger.error(f"Error creating item {item_data['sku']}: {e}")

    logger.info(f"Created {len(created_items)} demo items")

    # Create sales for sold items
    sold_items = [item for item in created_items if item['listing_status'] == 'Sold']

    for item in sold_items:
        try:
            sale_data = {
                'order_id': f"ORD-{random.randint(10000, 99999)}",
                'platform': item['platforms'][0] if item['platforms'] else 'Vinted',
                'item_id': item['id'],
                'item_name': item['item_name'],
                'sale_price': item['sale_price'],
                'fees': item['fees_estimate'],
                'shipping_cost': item['shipping_cost'],
                'buyer_paid_shipping': True,
                'date_sold': item['date_sold'],
                'date_shipped': (datetime.fromisoformat(item['date_sold']) + timedelta(days=1)).isoformat(),
                'tracking_number': f"TRK{random.randint(100000, 999999)}",
                'payout_status': 'Paid',
                'buyer_name': random.choice(['John Smith', 'Sarah Johnson', 'Mike Brown', 'Emma Davis']),
                'notes': 'Smooth transaction'
            }

            sale = db.create_sale(sale_data)
            if sale:
                logger.info(f"Created sale for item: {item['sku']}")

                # Create shipment record
                shipment_data = {
                    'sale_id': sale['id'],
                    'item_name': item['item_name'],
                    'platform': sale['platform'],
                    'buyer_name': sale['buyer_name'],
                    'buyer_address': '123 Main St, London, UK',
                    'status': 'Delivered',
                    'tracking_number': sale['tracking_number'],
                    'carrier': random.choice(['Royal Mail', 'DPD', 'Hermes']),
                    'shipped_at': sale['date_shipped'],
                    'delivered_at': (datetime.fromisoformat(sale['date_shipped']) + timedelta(days=2)).isoformat()
                }

                shipment = db.create_shipment(shipment_data)
                if shipment:
                    logger.info(f"Created shipment for sale: {sale['order_id']}")

        except Exception as e:
            logger.error(f"Error creating sale/shipment: {e}")

    # Create demo tasks
    demo_tasks = [
        {
            'title': 'List new Nike trainers on eBay',
            'description': 'Take photos and create listing for VINT-NIK-007',
            'priority': 'High',
            'status': 'Todo',
            'due_date': (datetime.now() + timedelta(days=2)).isoformat()
        },
        {
            'title': 'Follow up on pending payout',
            'description': 'Check Vinted for delayed payout on order ORD-12345',
            'priority': 'Medium',
            'status': 'In Progress',
            'due_date': (datetime.now() + timedelta(days=1)).isoformat()
        },
        {
            'title': 'Research trending items',
            'description': 'Check what trainers are selling well this month',
            'priority': 'Low',
            'status': 'Todo',
            'due_date': (datetime.now() + timedelta(days=7)).isoformat()
        },
        {
            'title': 'Update inventory spreadsheet',
            'description': 'Export and backup inventory data',
            'priority': 'Medium',
            'status': 'Done',
            'due_date': (datetime.now() - timedelta(days=1)).isoformat()
        }
    ]

    for task_data in demo_tasks:
        try:
            task = db.create_task(task_data)
            if task:
                logger.info(f"Created task: {task['title']}")
        except Exception as e:
            logger.error(f"Error creating task: {e}")

    # Create a demo return case
    if sold_items:
        try:
            return_data = {
                'item_name': 'Nike Air Max (Sample)',
                'platform': 'Vinted',
                'reason': 'Item not as described - buyer claimed size was wrong',
                'status': 'Resolved',
                'outcome': 'Partial Refund',
                'refund_amount': 20.00,
                'opened_at': (datetime.now() - timedelta(days=8)).isoformat(),
                'resolved_at': (datetime.now() - timedelta(days=2)).isoformat(),
                'notes': 'Offered 50% refund, buyer accepted'
            }

            return_case = db.create_return_case(return_data)
            if return_case:
                logger.info("Created demo return case")
        except Exception as e:
            logger.error(f"Error creating return case: {e}")

    logger.info("Database seed completed!")
    return {
        'success': True,
        'items_created': len(created_items),
        'sales_created': len(sold_items)
    }


if __name__ == "__main__":
    result = seed_demo_data()
    print(f"Seed completed: {result}")
