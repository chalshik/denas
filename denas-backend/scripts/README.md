# Denas Backend Scripts

This directory contains utility scripts for managing the Denas backend development environment.

## Available Scripts

### Development Environment
- **`start.sh`** - Start the development environment with Docker
- **`stop.sh`** - Stop all running containers
- **`reset-db.sh`** - Reset the database (clears all data)
- **`run-with-env.sh`** - Run commands with environment variables loaded
- **`start-supabase.sh`** - Start Supabase services

### Testing & Data
- **`add-test-products.sh`** - Add sample products for testing (NEW)
- **`remove-test-products.sh`** - Remove test products from database (NEW)

## Usage

### Starting the Development Environment
```bash
# Start backend services
./scripts/start.sh

# Stop backend services  
./scripts/stop.sh
```

### Adding Test Products
```bash
# Make sure backend is running first
./scripts/start.sh

# Add test products to database
./scripts/add-test-products.sh

# Remove test products (cleanup)
./scripts/remove-test-products.sh
```

## Test Products Script Details

The `add-test-products.sh` script adds sample products for testing the catalog functionality:

**Features:**
- ✅ Adds 8 Electronics products (Category ID: 1)
- ✅ Adds 8 Books products (Category ID: 2) 
- ✅ No images included (perfect for testing without media dependencies)
- ✅ Realistic product data with prices, descriptions, stock quantities
- ✅ Mix of IN_STOCK and PRE_ORDER availability types
- ✅ Colored output for easy monitoring
- ✅ Error handling and status checks

**Sample Products Added:**
- **Electronics**: Smartphones, Laptops, Headphones, Smartwatches, etc.
- **Books**: Programming guides, Tech handbooks, Development resources, etc.

**Requirements:**
- Backend must be running (`./scripts/start.sh`)
- `curl` and `jq` must be installed
- Categories with ID 1 and 2 must exist in database

**Output:**
```
🚀 Adding test products to Denas Backend...
ℹ️  Checking if backend is running...
✅ Backend is running!
ℹ️  Adding Category 1 (Electronics) products...
✅ Created: Smartphone Pro Max
✅ Created: Wireless Headphones
...
🎉 Test products added successfully!
```

Perfect for testing:
- Frontend catalog display
- Category filtering
- Search functionality  
- Price filtering
- Infinite scrolling
- Product cards without images

## Cleanup Script

The `remove-test-products.sh` script removes all test products added by the add script:

**Features:**
- ✅ Identifies test products by name
- ✅ Safely removes only test products (preserves real data)
- ✅ Provides detailed deletion report
- ✅ Colored output for easy monitoring
- ✅ Error handling for failed deletions

**Usage:**
```bash
# Remove all test products
./scripts/remove-test-products.sh
```

This is perfect for:
- Cleaning up after testing
- Resetting test environment
- Preparing for fresh test data 