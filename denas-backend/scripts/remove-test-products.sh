#!/bin/bash

# Remove Test Products Script for Denas Backend
# This script removes all test products added by add-test-products.sh

set -e  # Exit on any error

echo "🗑️  Removing test products from Denas Backend..."

# Configuration
API_URL="http://localhost:8000/api/v1"

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

# Test product names to identify and remove
TEST_PRODUCT_NAMES=(
    "Smartphone Pro Max"
    "Wireless Headphones" 
    "Laptop Gaming Edition"
    "Smartwatch Series X"
    "Tablet Pro 12-inch"
    "Bluetooth Speaker"
    "Wireless Charger"
    "4K Security Camera"
    "The Art of Programming"
    "Machine Learning Fundamentals"
    "Web Development Mastery"
    "Database Design Patterns"
    "Cybersecurity Handbook"
    "Cloud Computing Guide"
    "Mobile App Development"
    "DevOps Practices"
)

# Function to delete a product by ID
delete_product() {
    local product_id="$1"
    local product_name="$2"
    
    print_info "Deleting product: $product_name (ID: $product_id)"
    
    # Make API call to delete product
    response=$(curl -s -X DELETE \
        "$API_URL/products/$product_id" \
        -w "%{http_code}")
    
    # Extract HTTP status code
    http_code="${response: -3}"
    
    if [ "$http_code" -eq 200 ] || [ "$http_code" -eq 204 ]; then
        print_success "Deleted: $product_name"
        return 0
    else
        print_warning "Failed to delete: $product_name (HTTP $http_code)"
        return 1
    fi
}

# Get all products and find test products to delete
print_info "Fetching all products to identify test products..."
all_products=$(curl -s "$API_URL/products?limit=1000" | jq -r '.items[]? // empty')

if [ -z "$all_products" ]; then
    print_warning "No products found in database"
    exit 0
fi

deleted_count=0
failed_count=0

# Find and delete test products
for test_name in "${TEST_PRODUCT_NAMES[@]}"; do
    # Find product ID by name
    product_info=$(echo "$all_products" | jq -r "select(.name == \"$test_name\") | \"\(.id)|\(.name)\"" 2>/dev/null || echo "")
    
    if [ -n "$product_info" ]; then
        product_id=$(echo "$product_info" | cut -d'|' -f1)
        product_name=$(echo "$product_info" | cut -d'|' -f2)
        
        if delete_product "$product_id" "$product_name"; then
            ((deleted_count++))
        else
            ((failed_count++))
        fi
        
        sleep 0.3  # Small delay to avoid overwhelming the API
    else
        print_info "Test product not found: $test_name (might already be deleted)"
    fi
done

# Summary
print_info "Fetching updated product count..."
remaining_products=$(curl -s "$API_URL/products?limit=1000" | jq '.items | length' 2>/dev/null || echo "Unknown")

echo ""
if [ $deleted_count -gt 0 ]; then
    print_success "🎉 Test products cleanup completed!"
else
    print_warning "🤔 No test products were found to delete"
fi

echo -e "${GREEN}📊 Summary:${NC}"
echo -e "   • Products deleted: $deleted_count"
echo -e "   • Failed deletions: $failed_count"
echo -e "   • Remaining products: $remaining_products"
echo -e "   • API URL: $API_URL"
echo ""

if [ $deleted_count -gt 0 ]; then
    print_info "Database cleaned up successfully! You can now add fresh test data with ./scripts/add-test-products.sh"
else
    print_info "Run ./scripts/add-test-products.sh first to add test products, then use this script to clean them up."
fi 