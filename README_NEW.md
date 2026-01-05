# Awab Reselling Dashboard

> A comprehensive personal reselling command center with multi-platform support and Vinted integration.

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Status](https://img.shields.io/badge/status-beta-yellow)
![License](https://img.shields.io/badge/license-AGPL--3.0-green)

---

## What is This?

**Awab Reselling Dashboard** is a full-featured inventory and sales management system for resellers. Track your purchases, listings, sales, shipments, returns, and profits all in one place.

### Key Features

- **Inventory Management** - SKU-based item tracking with purchase price, sale price, fees, and automatic profit/ROI calculations
- **Sales Tracking** - Record sales with platform, buyer details, payout status, and shipping
- **Shipping Queue** - Manage dispatch workflow with tracking numbers and carrier info
- **Returns Management** - Track return cases and resolutions
- **Task Management** - Workflow tasks with priorities and due dates
- **Multi-Platform** - Support for Vinted, eBay, Depop, and more
- **Vinted Integration** - Automatically import items from Vinted searches (optional)
- **Analytics** - Profit tracking, ROI analysis, best brands/categories

---

## Quick Start

### Prerequisites

- Python 3.11+
- Supabase account (free tier works)

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd awab-reselling-dashboard

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add your Supabase credentials

# Seed demo data (optional)
python seed_data.py

# Run the application
python vinted_notifications.py
```

### Access

Open your browser to `http://localhost:8000`

---

## Environment Variables

Create a `.env` file in the project root:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
```

Get these from your Supabase project dashboard under Settings → API.

---

## Features Guide

### Inventory

Track all your items with:
- SKU, name, category, brand, size, condition
- Purchase price and date
- Sale price and profit calculations
- Listing status (Draft/Listed/Sold/Returned/Archived)
- Multi-platform support
- Photo storage
- Notes field

**Navigate:** Dashboard → Inventory

### Sales

Record sales with:
- Order ID and platform
- Sale price, fees, shipping cost
- Net profit calculation
- Buyer information
- Payout status
- Tracking numbers

**Navigate:** Dashboard → Sales

### Shipping

Manage dispatch with:
- Pending shipments queue
- Status tracking (Pending/Packed/Shipped/Delivered)
- Tracking numbers and carriers
- Buyer addresses

**Navigate:** Dashboard → Shipping

### Returns

Handle returns with:
- Reason tracking
- Status workflow (Open/In Progress/Resolved/Rejected)
- Outcome recording (Refunded/Replaced/etc.)
- Refund amounts
- Resolution notes

**Navigate:** Dashboard → Returns

### Tasks

Organize workflow with:
- Task list with priorities (Low/Medium/High/Urgent)
- Status tracking (Todo/In Progress/Done/Cancelled)
- Due dates
- Link tasks to items or sales

**Navigate:** Dashboard → Tasks

---

## Vinted Integration

The dashboard includes optional Vinted integration to automatically import items from your Vinted searches.

### How It Works

1. **Enable Integration**
   - Go to: Dashboard → Vinted Integration
   - Click "Enable Integration"
   - Test connection

2. **Add Search Queries**
   - Copy a Vinted search URL (e.g., `https://www.vinted.co.uk/catalog?search_text=nike`)
   - Paste into "Sync Query" form
   - Click "Sync Now"

3. **Review Imported Items**
   - Items appear in Inventory with status="Draft"
   - Review each item
   - Set purchase price
   - Change status to "Listed" when ready

### Data Mapping

| Vinted Field | Dashboard Field | Notes |
|--------------|----------------|-------|
| Item ID | vinted_item_id | For tracking |
| Title | Item Name | - |
| Brand | Brand | - |
| Size | Size | - |
| Price | Sale Price | Suggested price |
| Photos | Photos | Array of URLs |

**SKU Generated:** `VINT-{BRAND}-{ID}`
**Status:** Set to "Draft" for review

### Safety Features

- Banwords filtering (skip items with certain words)
- Country allowlist (optional)
- Duplicate detection
- Error handling (doesn't crash if Vinted is down)
- Integration logs for debugging

---

## Architecture

```
Flask Web App
    ↓
Database Layer (database.py)
    ↓
Supabase PostgreSQL

Vinted Integration (optional)
    ↓
VintedAdapter → VintedNormalizer
    ↓
pyVintedVN (Vinted API client)
```

---

## Database Schema

### Tables

- **items** - Inventory with profit/ROI calculations
- **sales** - Sales records with net profit
- **shipments** - Shipping tracking
- **return_cases** - Returns and disputes
- **tasks** - Workflow management
- **vinted_integration_logs** - Integration events
- **settings** - Configuration

### Security

- Row Level Security (RLS) enabled on all tables
- Policies allow authenticated users to manage their data
- For multi-user: Add per-user policies

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Python 3.11+, Flask |
| Database | Supabase (PostgreSQL) |
| Frontend | Bootstrap 5, Jinja2 |
| Background Jobs | APScheduler |
| External APIs | pyVintedVN |

---

## Development

### Project Structure

```
├── database.py                 # Supabase database layer
├── seed_data.py               # Demo data generator
├── integrations/
│   └── vinted/               # Vinted integration module
│       ├── adapter.py        # High-level wrapper
│       └── normalizer.py     # Data conversion
├── pyVintedVN/               # Vinted API client (preserved)
├── web_ui_plugin/
│   ├── web_ui.py            # Flask routes
│   ├── templates/           # Jinja2 templates
│   └── static/              # CSS, JS
└── vinted_notifications.py   # Main entry point
```

### Adding Features

1. Add database functions in `database.py`
2. Create route in `web_ui_plugin/web_ui.py`
3. Create template in `web_ui_plugin/templates/`
4. Update navigation in `base_new.html`

### Running Tests

```bash
# Test database connection
python -c "import database as db; print(db.get_supabase())"

# Seed demo data
python seed_data.py

# Test Vinted integration
python -c "from integrations.vinted import VintedAdapter; a = VintedAdapter(); print(a.test_connection())"
```

---

## Documentation

- **[TRANSFORMATION_SUMMARY.md](TRANSFORMATION_SUMMARY.md)** - Complete transformation details
- **[IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)** - Step-by-step implementation guide
- **[LICENSE](LICENSE)** - AGPL-3.0 license

---

## Roadmap

### Phase 1: Foundation ✅
- [x] Database schema
- [x] Supabase integration
- [x] Vinted integration isolation
- [x] UI rebranding
- [x] Inventory template
- [x] Demo data

### Phase 2: Core Features (In Progress)
- [ ] All route implementations
- [ ] All page templates
- [ ] CRUD operations complete
- [ ] CSV export

### Phase 3: Advanced Features
- [ ] Charts and analytics
- [ ] Multi-user authentication
- [ ] eBay integration
- [ ] Depop integration
- [ ] Mobile app

---

## Contributing

This is a personal project, but contributions are welcome:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).

See [LICENSE](LICENSE) for details.

---

## Acknowledgements

- **pyVintedVN** - Vinted API client by [@herissondev](https://github.com/herissondev)
- **Bootstrap** - UI framework
- **Supabase** - Database and backend infrastructure

---

## Support

For questions or issues:
1. Check [TRANSFORMATION_SUMMARY.md](TRANSFORMATION_SUMMARY.md) for detailed documentation
2. Check [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) for troubleshooting
3. Open an issue on GitHub

---

Made with ☕ by Awab
