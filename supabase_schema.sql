/*
  # Awab Reselling Dashboard - Initial Schema

  1. New Tables
    - `items` - Inventory management (SKU, purchase, listing, sale tracking)
    - `sales` - Sales records with profit calculations
    - `shipments` - Shipping/dispatch queue
    - `return_cases` - Returns and disputes tracking
    - `tasks` - Workflow task management
    - `vinted_integration_logs` - Integration sync logs
    - `settings` - Application configuration

  2. Security
    - Enable RLS on all tables
    - Add policies for authenticated user access

  3. Features
    - Profit/ROI calculations
    - Multi-platform support
    - Vinted integration bridge
*/

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Items (Inventory) Table
CREATE TABLE IF NOT EXISTS items (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  sku text UNIQUE NOT NULL,
  item_name text NOT NULL,
  category text,
  size text,
  condition text CHECK (condition IN ('New', 'Like New', 'Good', 'Fair', 'Poor')),
  brand text,
  platforms text[], -- Array of platforms (Vinted, eBay, Depop, etc.)
  listing_status text DEFAULT 'Draft' CHECK (listing_status IN ('Draft', 'Listed', 'Sold', 'Returned', 'Archived')),
  purchase_price numeric(10, 2),
  fees_estimate numeric(10, 2) DEFAULT 0,
  shipping_paid_by text CHECK (shipping_paid_by IN ('Buyer', 'Seller', 'Split')),
  shipping_cost numeric(10, 2) DEFAULT 0,
  sale_price numeric(10, 2),
  profit numeric(10, 2) GENERATED ALWAYS AS (
    COALESCE(sale_price, 0) - COALESCE(purchase_price, 0) - COALESCE(fees_estimate, 0) -
    CASE WHEN shipping_paid_by = 'Seller' THEN COALESCE(shipping_cost, 0) ELSE 0 END
  ) STORED,
  roi_percent numeric(5, 2) GENERATED ALWAYS AS (
    CASE
      WHEN COALESCE(purchase_price, 0) > 0 THEN
        ((COALESCE(sale_price, 0) - COALESCE(purchase_price, 0) - COALESCE(fees_estimate, 0) -
          CASE WHEN shipping_paid_by = 'Seller' THEN COALESCE(shipping_cost, 0) ELSE 0 END) / purchase_price) * 100
      ELSE 0
    END
  ) STORED,
  date_purchased timestamptz,
  date_listed timestamptz,
  date_sold timestamptz,
  location text,
  notes text,
  photos text[], -- Array of photo URLs
  vinted_item_id text, -- Link to original Vinted item if imported
  vinted_query_id integer, -- Link to Vinted query that found it
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Sales Table
CREATE TABLE IF NOT EXISTS sales (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  order_id text NOT NULL,
  platform text NOT NULL,
  item_id uuid REFERENCES items(id) ON DELETE CASCADE,
  item_name text NOT NULL,
  sale_price numeric(10, 2) NOT NULL,
  fees numeric(10, 2) DEFAULT 0,
  shipping_cost numeric(10, 2) DEFAULT 0,
  buyer_paid_shipping boolean DEFAULT false,
  net_profit numeric(10, 2) GENERATED ALWAYS AS (
    sale_price - COALESCE(fees, 0) - CASE WHEN NOT buyer_paid_shipping THEN COALESCE(shipping_cost, 0) ELSE 0 END
  ) STORED,
  date_sold timestamptz DEFAULT now(),
  date_shipped timestamptz,
  tracking_number text,
  payout_status text DEFAULT 'Pending' CHECK (payout_status IN ('Pending', 'Processing', 'Paid', 'Failed')),
  buyer_name text,
  buyer_email text,
  notes text,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Shipments Table
CREATE TABLE IF NOT EXISTS shipments (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  sale_id uuid REFERENCES sales(id) ON DELETE CASCADE,
  item_name text NOT NULL,
  platform text NOT NULL,
  buyer_name text,
  buyer_address text,
  status text DEFAULT 'Pending' CHECK (status IN ('Pending', 'Packed', 'Shipped', 'Delivered', 'Failed')),
  tracking_number text,
  carrier text,
  shipped_at timestamptz,
  delivered_at timestamptz,
  notes text,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Return Cases Table
CREATE TABLE IF NOT EXISTS return_cases (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  sale_id uuid REFERENCES sales(id) ON DELETE SET NULL,
  item_name text NOT NULL,
  platform text NOT NULL,
  reason text NOT NULL,
  status text DEFAULT 'Open' CHECK (status IN ('Open', 'In Progress', 'Resolved', 'Rejected')),
  outcome text CHECK (outcome IN ('Refunded', 'Replaced', 'Rejected', 'Partial Refund')),
  refund_amount numeric(10, 2),
  opened_at timestamptz DEFAULT now(),
  resolved_at timestamptz,
  notes text,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Tasks Table
CREATE TABLE IF NOT EXISTS tasks (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  title text NOT NULL,
  description text,
  priority text DEFAULT 'Medium' CHECK (priority IN ('Low', 'Medium', 'High', 'Urgent')),
  status text DEFAULT 'Todo' CHECK (status IN ('Todo', 'In Progress', 'Done', 'Cancelled')),
  due_date timestamptz,
  related_item_id uuid REFERENCES items(id) ON DELETE SET NULL,
  related_sale_id uuid REFERENCES sales(id) ON DELETE SET NULL,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Vinted Integration Logs Table
CREATE TABLE IF NOT EXISTS vinted_integration_logs (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  event_type text NOT NULL,
  status text CHECK (status IN ('Success', 'Error', 'Warning')),
  message text,
  data jsonb,
  created_at timestamptz DEFAULT now()
);

-- Settings Table
CREATE TABLE IF NOT EXISTS settings (
  key text PRIMARY KEY,
  value text NOT NULL,
  description text,
  updated_at timestamptz DEFAULT now()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_items_listing_status ON items(listing_status);
CREATE INDEX IF NOT EXISTS idx_items_date_purchased ON items(date_purchased);
CREATE INDEX IF NOT EXISTS idx_items_vinted_item_id ON items(vinted_item_id);
CREATE INDEX IF NOT EXISTS idx_sales_date_sold ON sales(date_sold);
CREATE INDEX IF NOT EXISTS idx_sales_platform ON sales(platform);
CREATE INDEX IF NOT EXISTS idx_shipments_status ON shipments(status);
CREATE INDEX IF NOT EXISTS idx_return_cases_status ON return_cases(status);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_vinted_logs_created_at ON vinted_integration_logs(created_at);

-- Enable Row Level Security
ALTER TABLE items ENABLE ROW LEVEL SECURITY;
ALTER TABLE sales ENABLE ROW LEVEL SECURITY;
ALTER TABLE shipments ENABLE ROW LEVEL SECURITY;
ALTER TABLE return_cases ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE vinted_integration_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE settings ENABLE ROW LEVEL SECURITY;

-- RLS Policies (allowing all operations for authenticated users for now)
-- In production, you'd want more granular policies

CREATE POLICY "Users can manage items"
  ON items FOR ALL
  TO authenticated
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Users can manage sales"
  ON sales FOR ALL
  TO authenticated
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Users can manage shipments"
  ON shipments FOR ALL
  TO authenticated
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Users can manage return cases"
  ON return_cases FOR ALL
  TO authenticated
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Users can manage tasks"
  ON tasks FOR ALL
  TO authenticated
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Users can view integration logs"
  ON vinted_integration_logs FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "System can insert integration logs"
  ON vinted_integration_logs FOR INSERT
  TO authenticated
  WITH CHECK (true);

CREATE POLICY "Users can manage settings"
  ON settings FOR ALL
  TO authenticated
  USING (true)
  WITH CHECK (true);

-- Insert default settings
INSERT INTO settings (key, value, description) VALUES
  ('vinted_integration_enabled', 'false', 'Enable Vinted integration'),
  ('vinted_last_sync', '0', 'Last sync timestamp'),
  ('vinted_sync_interval', '60', 'Sync interval in seconds'),
  ('default_currency', 'GBP', 'Default currency'),
  ('vinted_fee_percent', '10', 'Vinted platform fee percentage'),
  ('ebay_fee_percent', '12.8', 'eBay platform fee percentage'),
  ('depop_fee_percent', '10', 'Depop platform fee percentage'),
  ('default_shipping_cost', '3.50', 'Default shipping cost'),
  ('items_per_page', '50', 'Items per page in tables')
ON CONFLICT (key) DO NOTHING;
