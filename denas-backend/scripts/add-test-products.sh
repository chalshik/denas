#!/bin/bash

# Add Test Products Script for Denas Backend
# This script adds sample products for testing purposes only
# Uses categories with ID 1 and 2, no images included

set -e  # Exit on any error

echo "🚀 Adding test products to Denas Backend..."

# Configuration
API_URL="http://localhost:8000/api/v1"
ADMIN_PHONE="+1234567890"  # Default admin phone for authentication
ADMIN_PASSWORD="admin123"  # Default admin password

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if backend is running
print_info "Checking if backend is running..."
if ! curl -s "$API_URL/health" > /dev/null 2>&1; then
    print_error "Backend is not running! Please start it first with: ./scripts/start.sh"
    exit 1
fi
print_success "Backend is running!"

# Test products data for Category 1 (Electronics)
CATEGORY_1_PRODUCTS=(
    '{"name": "Smartphone Pro Max", "description": "Latest flagship smartphone with advanced features", "price": 999.99, "category_id": 1, "stock_quantity": 50, "availability_type": "IN_STOCK", "is_active": true}'
    '{"name": "Wireless Headphones", "description": "Premium noise-cancelling wireless headphones", "price": 249.99, "category_id": 1, "stock_quantity": 30, "availability_type": "IN_STOCK", "is_active": true}'
    '{"name": "Laptop Gaming Edition", "description": "High-performance gaming laptop with RTX graphics", "price": 1599.99, "category_id": 1, "stock_quantity": 15, "availability_type": "IN_STOCK", "is_active": true}'
    '{"name": "Smartwatch Series X", "description": "Advanced fitness and health tracking smartwatch", "price": 399.99, "category_id": 1, "stock_quantity": 25, "availability_type": "IN_STOCK", "is_active": true}'
    '{"name": "Tablet Pro 12-inch", "description": "Professional tablet for creative work and productivity", "price": 799.99, "category_id": 1, "stock_quantity": 20, "availability_type": "PRE_ORDER", "is_active": true}'
    '{"name": "Bluetooth Speaker", "description": "Portable waterproof Bluetooth speaker with rich sound", "price": 89.99, "category_id": 1, "stock_quantity": 100, "availability_type": "IN_STOCK", "is_active": true}'
    '{"name": "Wireless Charger", "description": "Fast wireless charging pad for smartphones", "price": 39.99, "category_id": 1, "stock_quantity": 75, "availability_type": "IN_STOCK", "is_active": true}'
    '{"name": "4K Security Camera", "description": "Smart home security camera with night vision", "price": 129.99, "category_id": 1, "stock_quantity": 40, "availability_type": "IN_STOCK", "is_active": true}'
)

# Test products data for Category 2 (Books)
CATEGORY_2_PRODUCTS=(
    '{"name": "The Art of Programming", "description": "Comprehensive guide to software development best practices", "price": 49.99, "category_id": 2, "stock_quantity": 200, "availability_type": "IN_STOCK", "is_active": true}'
    '{"name": "Machine Learning Fundamentals", "description": "Introduction to AI and machine learning concepts", "price": 59.99, "category_id": 2, "stock_quantity": 150, "availability_type": "IN_STOCK", "is_active": true}'
    '{"name": "Web Development Mastery", "description": "Complete guide to modern web development", "price": 44.99, "category_id": 2, "stock_quantity": 180, "availability_type": "IN_STOCK", "is_active": true}'
    '{"name": "Database Design Patterns", "description": "Advanced database architecture and optimization", "price": 54.99, "category_id": 2, "stock_quantity": 120, "availability_type": "IN_STOCK", "is_active": true}'
    '{"name": "Cybersecurity Handbook", "description": "Essential guide to information security", "price": 39.99, "category_id": 2, "stock_quantity": 90, "availability_type": "IN_STOCK", "is_active": true}'
    '{"name": "Cloud Computing Guide", "description": "Modern cloud architecture and deployment strategies", "price": 52.99, "category_id": 2, "stock_quantity": 110, "availability_type": "PRE_ORDER", "is_active": true}'
    '{"name": "Mobile App Development", "description": "Cross-platform mobile development with React Native", "price": 47.99, "category_id": 2, "stock_quantity": 160, "availability_type": "IN_STOCK", "is_active": true}'
    '{"name": "DevOps Practices", "description": "Continuous integration and deployment strategies", "price": 41.99, "category_id": 2, "stock_quantity": 130, "availability_type": "IN_STOCK", "is_active": true}'
)

# Function to add a product
add_product() {
    local product_data="$1"
    local product_name=$(echo "$product_data" | jq -r '.name')
    
    print_info "Adding product: $product_name"
    
    # Make API call to create product
    response=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d "$product_data" \
        "$API_URL/products" \
        -w "%{http_code}")
    
    # Extract HTTP status code
    http_code="${response: -3}"
    response_body="${response%???}"
    
    if [ "$http_code" -eq 201 ] || [ "$http_code" -eq 200 ]; then
        print_success "Created: $product_name"
    else
        print_warning "Failed to create: $product_name (HTTP $http_code)"
        if [ -n "$response_body" ]; then
            echo "Response: $response_body"
        fi
    fi
}

# Add all Category 1 products (Electronics)
print_info "Adding Category 1 (Electronics) products..."
for product in "${CATEGORY_1_PRODUCTS[@]}"; do
    add_product "$product"
    sleep 0.5  # Small delay to avoid overwhelming the API
done

print_success "Finished adding Category 1 products!"

# Add all Category 2 products (Books)  
print_info "Adding Category 2 (Books) products..."
for product in "${CATEGORY_2_PRODUCTS[@]}"; do
    add_product "$product"
    sleep 0.5  # Small delay to avoid overwhelming the API
done

print_success "Finished adding Category 2 products!"

# Summary
print_info "Fetching product summary..."
total_products=$(curl -s "$API_URL/products?limit=1000" | jq '.items | length' 2>/dev/null || echo "Unknown")

echo ""
print_success "🎉 Test products added successfully!"
echo -e "${GREEN}📊 Summary:${NC}"
echo -e "   • Total products in database: $total_products"
echo -e "   • Category 1 products added: ${#CATEGORY_1_PRODUCTS[@]}"
echo -e "   • Category 2 products added: ${#CATEGORY_2_PRODUCTS[@]}"
echo -e "   • API URL: $API_URL"
echo ""
print_info "You can now test the catalog functionality in the frontend!"
print_warning "Note: These are test products without images - perfect for testing the catalog interface." 