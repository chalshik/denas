'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@heroui/button';
import { Input } from '@heroui/input';
import { Select, SelectItem } from '@heroui/select';
import { Table, TableHeader, TableColumn, TableBody, TableRow, TableCell } from '@heroui/table';

import { Pagination } from '@heroui/react';
import { Product, ProductCatalog, Category, ProductWithDetails } from '@/types';
import { useCategories } from '@/hooks/useCategories';
import { useProducts } from '@/hooks/useProducts';

interface ProductsTableProps {
  onDelete: (productId: number) => void;
  onViewDetails?: (product: Product | ProductCatalog | ProductWithDetails) => void;
  onDataChange?: () => void; // Callback when data changes (for parent refresh)
}

export default function ProductsTable({ 
  onDelete, 
  onViewDetails,
  onDataChange
}: ProductsTableProps) {
  // Input states (immediate updates for UI)
  const [searchInput, setSearchInput] = useState('');
  const [minPriceInput, setMinPriceInput] = useState('');
  const [maxPriceInput, setMaxPriceInput] = useState('');
  
  // Debounced states (delayed updates for API calls)
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [products, setProducts] = useState<ProductWithDetails[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  
  // Server-side filters
  const [filters, setFilters] = useState({
    categoryId: undefined as number | undefined,
    minPrice: undefined as number | undefined,
    maxPrice: undefined as number | undefined,
  });
  
  // Column visibility state
  const [visibleColumns, setVisibleColumns] = useState({
    name: true,
    price: true,
    category: true,
    status: true,
    actions: true, // Always visible
  });
  
  const { categories = [], fetchCategories } = useCategories();
  const { fetchAdminProducts, loading } = useProducts();
  
  // Page size options
  const pageSizeOptions = [
    { label: '10 per page', value: '10' },
    { label: '20 per page', value: '20' },
    { label: '50 per page', value: '50' },
    { label: '100 per page', value: '100' },
  ];

  // Column options for visibility toggle
  const columnOptions = [
    { key: 'name', label: 'Name', required: true },
    { key: 'price', label: 'Price', required: false },
    { key: 'category', label: 'Category', required: false },
    { key: 'status', label: 'Status', required: false },
    { key: 'actions', label: 'Actions', required: true },
  ];

  // Debounce search term
  useEffect(() => {
    const timer = setTimeout(() => {
      setSearchTerm(searchInput);
    }, 300);

    return () => clearTimeout(timer);
  }, [searchInput]);

  // Debounce price filters
  useEffect(() => {
    const timer = setTimeout(() => {
      const minPrice = minPriceInput ? parseFloat(minPriceInput) : undefined;
      const maxPrice = maxPriceInput ? parseFloat(maxPriceInput) : undefined;
      
      setFilters(prev => ({
        ...prev,
        minPrice,
        maxPrice
      }));
    }, 500);

    return () => clearTimeout(timer);
  }, [minPriceInput, maxPriceInput]);

  // Handle column visibility change
  const handleColumnVisibilityChange = (columnKey: string, isVisible: boolean) => {
    setVisibleColumns(prev => ({
      ...prev,
      [columnKey]: isVisible
    }));
  };

  // Get selected column keys for the dropdown
  const selectedColumnKeys = Object.entries(visibleColumns)
    .filter(([_, isVisible]) => isVisible)
    .map(([key, _]) => key);

  // Create a lookup map for categories
  const categoryMap = React.useMemo(() => {
    const map: Record<number, string> = {};
    categories.forEach(cat => {
      map[cat.id] = cat.name;
    });
    return map;
  }, [categories]);

  // Fetch categories on mount
  useEffect(() => {
    fetchCategories();
  }, []);

  // Fetch products when pagination parameters or filters change
  const loadProducts = async () => {
    try {
      const { products: fetchedProducts, total } = await fetchAdminProducts(
        currentPage, 
        pageSize, 
        true, // Always include inactive products for admin
        filters
      );
      setProducts(fetchedProducts);
      setTotalCount(total);
    } catch (error) {
      console.error('Failed to fetch products:', error);
    }
  };

  useEffect(() => {
    loadProducts();
  }, [currentPage, pageSize, filters]);

  // Reset to page 1 when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [filters.categoryId, filters.minPrice, filters.maxPrice]);

  // Refresh data when external changes occur
  const handleRefresh = () => {
    loadProducts();
    onDataChange?.(); // Notify parent component
  };

  // Handle page size change
  const handlePageSizeChange = (value: string) => {
    const newPageSize = parseInt(value);
    setPageSize(newPageSize);
    setCurrentPage(1); // Reset to first page when changing page size
  };

  // Handle page change
  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  // Handle filter changes
  const handleCategoryFilter = (categoryId: string) => {
    setFilters(prev => ({
      ...prev,
      categoryId: categoryId ? parseInt(categoryId) : undefined
    }));
  };



  // Clear all filters
  const clearFilters = () => {
    setSearchInput('');
    setMinPriceInput('');
    setMaxPriceInput('');
    setFilters({
      categoryId: undefined,
      minPrice: undefined,
      maxPrice: undefined,
    });
  };

  // Filter products by search term
  const filteredProducts = products.filter(product =>
    (product.name?.toLowerCase() || '').includes(searchTerm.toLowerCase()) ||
    (getCategoryName(product).toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const getCategoryName = (product: ProductWithDetails): string => {
    // Check if it has full category object
    if (product.category?.name) {
      return product.category.name;
    }
    // Use category lookup map
    return categoryMap[product.category_id] || `Category ${product.category_id}`;
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(price);
  };

  const getAvailabilityColor = (availability: string) => {
    switch (availability) {
      case 'IN_STOCK':
        return 'text-green-600 bg-green-100';
      case 'PRE_ORDER':
        return 'text-yellow-600 bg-yellow-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const handleDeleteProduct = async (productId: number) => {
    await onDelete(productId);
    handleRefresh(); // Refresh the table after deletion
  };

  // Calculate total pages
  const totalPages = Math.ceil(totalCount / pageSize);

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
      
        
        {/* Filter Controls - Single Row */}
        <div className="flex items-center gap-3 mb-4">
          <Select
            placeholder="All categories"
            selectedKeys={filters.categoryId ? [String(filters.categoryId)] : []}
            onSelectionChange={(keys) => {
              const selectedKey = Array.from(keys)[0] as string;
              handleCategoryFilter(selectedKey);
            }}
            className="w-48"
            size="sm"
            variant="bordered"
          >
            {[
              <SelectItem key="">All categories</SelectItem>,
              ...categories.map(category => (
                <SelectItem key={String(category.id)}>
                  {category.name}
                </SelectItem>
              ))
            ]}
          </Select>

          <Input
            placeholder="Min price"
            type="number"
            min="0"
            step="0.01"
            value={minPriceInput}
            onValueChange={setMinPriceInput}
            startContent={<span className="text-gray-400">$</span>}
            className="w-32"
            size="sm"
            variant="bordered"
          />

          <Input
            placeholder="Max price"
            type="number"
            min="0"
            step="0.01"
            value={maxPriceInput}
            onValueChange={setMaxPriceInput}
            startContent={<span className="text-gray-400">$</span>}
            className="w-32"
            size="sm"
            variant="bordered"
          />

          <Select
            selectedKeys={selectedColumnKeys}
            onSelectionChange={(keys) => {
              const newSelectedKeys = Array.from(keys) as string[];
              columnOptions.forEach(column => {
                const isSelected = newSelectedKeys.includes(column.key);
                if (!column.required || isSelected) {
                  handleColumnVisibilityChange(column.key, isSelected);
                }
              });
            }}
            selectionMode="multiple"
            placeholder="Columns"
            className="w-32"
            size="sm"
            variant="bordered"
          >
            {columnOptions.map(column => (
              <SelectItem 
                key={column.key}
                isDisabled={column.required}
              >
                {column.label}
              </SelectItem>
            ))}
          </Select>
        </div>

        {/* Search and Controls Row */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <span>Rows per page:</span>
              <Select
                selectedKeys={[String(pageSize)]}
                onSelectionChange={(keys) => handlePageSizeChange(Array.from(keys)[0] as string)}
                className="w-16"
                size="sm"
                variant="bordered"
              >
                {pageSizeOptions.map(option => (
                  <SelectItem key={option.value}>
                    {option.value}
                  </SelectItem>
                ))}
              </Select>
            </div>
            
            <Input
              placeholder="Search products..."
              value={searchInput}
              onValueChange={setSearchInput}
              className="w-64"
              size="sm"
              variant="bordered"
              startContent={
                <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              }
            />
          </div>

        
        </div>
      </div>

      {/* Table */}
      <Table 
        aria-label="Products table"
        removeWrapper
        classNames={{
          th: "bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider px-6 py-3",
          td: "px-6 py-4 whitespace-nowrap text-sm text-gray-900",
          tbody: "bg-white divide-y divide-gray-200"
        }}
      >
        <TableHeader>
          {columnOptions
            .filter(column => visibleColumns[column.key as keyof typeof visibleColumns])
            .map(column => (
              <TableColumn key={column.key}>{column.label}</TableColumn>
            ))}
        </TableHeader>
        <TableBody 
          emptyContent={loading ? "Loading products..." : "No products found"}
          isLoading={loading}
        >
          {filteredProducts.map((product) => (
            <TableRow 
              key={product.id} 
              className="hover:bg-gray-50 cursor-pointer"
              onClick={() => onViewDetails?.(product)}
            >
              {[
                ...(visibleColumns.name ? [
                  <TableCell key="name">
                    <div>
                      <div className="font-medium text-gray-900">{product.name}</div>
                      {product.description && (
                        <div className="text-sm text-gray-500">
                          {product.description}
                    </div>
                  )}
                </div>
              </TableCell>
                ] : []),
                ...(visibleColumns.price ? [
                  <TableCell key="price">
                    <span className="font-semibold">
                      ${Number(product.price).toFixed(2)}
                </span>
              </TableCell>
                ] : []),
                ...(visibleColumns.category ? [
                  <TableCell key="category">
                    {getCategoryName(product)}
              </TableCell>
                ] : []),
                ...(visibleColumns.status ? [
                  <TableCell key="status">
                    <div className="flex flex-col gap-1">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        product.is_active 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                }`}>
                  {product.is_active ? 'Active' : 'Inactive'}
                </span>
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                  getAvailabilityColor(product.availability_type || 'IN_STOCK')
                }`}>
                  {(product.availability_type || 'IN_STOCK').replace('_', ' ')}
                </span>
                    </div>
              </TableCell>
                ] : []),
                ...(visibleColumns.actions ? [
                  <TableCell key="actions">
                    <Button
                      size="sm"
                      color="danger"
                      variant="flat"
                      onPress={() => handleDeleteProduct(product.id)}
                      onClick={(e) => e.stopPropagation()}
                    >
                      Delete
                    </Button>
              </TableCell>
                ] : [])
              ]}
            </TableRow>
          ))}
        </TableBody>
      </Table>

      {/* Footer with Pagination */}
      <div className="px-6 py-4 border-t border-gray-200">
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-700">
            Showing {((currentPage - 1) * pageSize) + 1} to {Math.min(currentPage * pageSize, totalCount)} of {totalCount} products
          </div>
          
          <div className="flex items-center gap-2">
            <Pagination
              total={totalPages}
              page={currentPage}
              onChange={handlePageChange}
              showControls
              color="primary"
              size="sm"
            />
          </div>
        </div>
      </div>
    </div>
  );
} 