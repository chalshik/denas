"use client";

import React, { useState, useEffect } from "react";
import { Button } from "@heroui/button";
import { Input } from "@heroui/input";
import { Select, SelectItem } from "@heroui/select";
import {
  Table,
  TableHeader,
  TableColumn,
  TableBody,
  TableRow,
  TableCell,
} from "@heroui/table";
import { Pagination } from "@heroui/react";

import { Product, ProductCatalog, ProductWithDetails } from "@/types";
import { useCategories } from "@/hooks/useCategories";
import { useProducts } from "@/hooks/useProducts";

interface ProductsTableProps {
  onDelete: (productId: number) => void;
  onViewDetails?: (
    product: Product | ProductCatalog | ProductWithDetails,
  ) => void;
  onDataChange?: () => void; // Callback when data changes (for parent refresh)
}

export default function ProductsTable({
  onDelete,
  onViewDetails,
  onDataChange,
}: ProductsTableProps) {
  // Input states (immediate updates for UI)
  const [searchInput, setSearchInput] = useState("");
  const [minPriceInput, setMinPriceInput] = useState("");
  const [maxPriceInput, setMaxPriceInput] = useState("");

  // Debounced states (delayed updates for API calls)
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [products, setProducts] = useState<ProductWithDetails[]>([]);
  const [totalCount, setTotalCount] = useState(0);

  // Server-side filters
  const [filters, setFilters] = useState({
    categoryId: undefined as number | undefined,
    minPrice: undefined as number | undefined,
    maxPrice: undefined as number | undefined,
    search: undefined as string | undefined,
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
    { label: "10 per page", value: "10" },
    { label: "20 per page", value: "20" },
    { label: "50 per page", value: "50" },
    { label: "100 per page", value: "100" },
  ];

  // Column options for visibility toggle
  const columnOptions = [
    { key: "name", label: "Name", required: true },
    { key: "price", label: "Price", required: false },
    { key: "category", label: "Category", required: false },
    { key: "status", label: "Status", required: false },
    { key: "actions", label: "Actions", required: true },
  ];

  // Debounce search term and update filters
  useEffect(() => {
    const timer = setTimeout(() => {
      setFilters((prev) => ({
        ...prev,
        search: searchInput.trim() || undefined,
      }));
    }, 300);

    return () => clearTimeout(timer);
  }, [searchInput]);

  // Debounce price filters
  useEffect(() => {
    const timer = setTimeout(() => {
      const minPrice = minPriceInput ? parseFloat(minPriceInput) : undefined;
      const maxPrice = maxPriceInput ? parseFloat(maxPriceInput) : undefined;

      setFilters((prev) => ({
        ...prev,
        minPrice,
        maxPrice,
      }));
    }, 500);

    return () => clearTimeout(timer);
  }, [minPriceInput, maxPriceInput]);

  // Handle column visibility change
  const handleColumnVisibilityChange = (
    columnKey: string,
    isVisible: boolean,
  ) => {
    setVisibleColumns((prev) => ({
      ...prev,
      [columnKey]: isVisible,
    }));
  };

  // Get selected column keys for the dropdown
  const selectedColumnKeys = Object.entries(visibleColumns)
    .filter(([_, isVisible]) => isVisible)
    .map(([key, _]) => key);

  // Create a lookup map for categories
  const categoryMap = React.useMemo(() => {
    const map: Record<number, string> = {};

    categories.forEach((cat) => {
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
        filters,
      );

      setProducts(fetchedProducts);
      setTotalCount(total);
    } catch (error) {
      console.error("Failed to fetch products:", error);
    }
  };

  useEffect(() => {
    loadProducts();
  }, [currentPage, pageSize, filters]);

  // Reset to page 1 when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [filters.categoryId, filters.minPrice, filters.maxPrice, filters.search]);

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
    setFilters((prev) => ({
      ...prev,
      categoryId: categoryId ? parseInt(categoryId) : undefined,
    }));
  };

  // Helper function to get category name
  const getCategoryName = (product: ProductWithDetails): string => {
    // Check if it has full category object
    if (product.category?.name) {
      return product.category.name;
    }

    // Use category lookup map
    return (
      categoryMap[product.category_id] || `Category ${product.category_id}`
    );
  };

  const getAvailabilityColor = (availability: string) => {
    switch (availability) {
      case "IN_STOCK":
        return "text-green-600 bg-green-100";
      case "PRE_ORDER":
        return "text-yellow-600 bg-yellow-100";
      default:
        return "text-gray-600 bg-gray-100";
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
            className="w-48"
            placeholder="All categories"
            selectedKeys={
              filters.categoryId ? [String(filters.categoryId)] : []
            }
            size="sm"
            variant="bordered"
            onSelectionChange={(keys) => {
              const selectedKey = Array.from(keys)[0] as string;

              handleCategoryFilter(selectedKey);
            }}
          >
            {[
              <SelectItem key="">All categories</SelectItem>,
              ...categories.map((category) => (
                <SelectItem key={String(category.id)}>
                  {category.name}
                </SelectItem>
              )),
            ]}
          </Select>

          <Input
            className="w-32"
            min="0"
            placeholder="Min price"
            size="sm"
            startContent={<span className="text-gray-400">$</span>}
            step="0.01"
            type="number"
            value={minPriceInput}
            variant="bordered"
            onValueChange={setMinPriceInput}
          />

          <Input
            className="w-32"
            min="0"
            placeholder="Max price"
            size="sm"
            startContent={<span className="text-gray-400">$</span>}
            step="0.01"
            type="number"
            value={maxPriceInput}
            variant="bordered"
            onValueChange={setMaxPriceInput}
          />

          <Select
            className="w-32"
            placeholder="Columns"
            selectedKeys={selectedColumnKeys}
            selectionMode="multiple"
            size="sm"
            variant="bordered"
            onSelectionChange={(keys) => {
              const newSelectedKeys = Array.from(keys) as string[];

              columnOptions.forEach((column) => {
                const isSelected = newSelectedKeys.includes(column.key);

                if (!column.required || isSelected) {
                  handleColumnVisibilityChange(column.key, isSelected);
                }
              });
            }}
          >
            {columnOptions.map((column) => (
              <SelectItem key={column.key} isDisabled={column.required}>
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
                className="w-16"
                selectedKeys={[String(pageSize)]}
                size="sm"
                variant="bordered"
                onSelectionChange={(keys) =>
                  handlePageSizeChange(Array.from(keys)[0] as string)
                }
              >
                {pageSizeOptions.map((option) => (
                  <SelectItem key={option.value}>{option.value}</SelectItem>
                ))}
              </Select>
            </div>

            <Input
              className="w-64"
              placeholder="Search products..."
              size="sm"
              startContent={
                <svg
                  className="w-4 h-4 text-gray-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                  />
                </svg>
              }
              value={searchInput}
              variant="bordered"
              onValueChange={setSearchInput}
            />
          </div>
        </div>
      </div>

      {/* Table */}
      <Table
        removeWrapper
        aria-label="Products table"
        classNames={{
          th: "bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider px-6 py-3",
          td: "px-6 py-4 whitespace-nowrap text-sm text-gray-900",
          tbody: "bg-white divide-y divide-gray-200",
        }}
      >
        <TableHeader>
          {columnOptions
            .filter(
              (column) =>
                visibleColumns[column.key as keyof typeof visibleColumns],
            )
            .map((column) => (
              <TableColumn key={column.key}>{column.label}</TableColumn>
            ))}
        </TableHeader>
        <TableBody
          emptyContent={loading ? "Loading products..." : "No products found"}
          isLoading={loading}
        >
          {products.map((product) => (
            <TableRow
              key={product.id}
              className="hover:bg-gray-50 cursor-pointer"
              onClick={() => onViewDetails?.(product)}
            >
              {[
                ...(visibleColumns.name
                  ? [
                      <TableCell key="name">
                        <div>
                          <div className="font-medium text-gray-900">
                            {product.name}
                          </div>
                          {product.description &&
                            product.description.trim() && (
                              <div className="text-sm text-gray-500">
                                {product.description}
                              </div>
                            )}
                        </div>
                      </TableCell>,
                    ]
                  : []),
                ...(visibleColumns.price
                  ? [
                      <TableCell key="price">
                        <span className="font-semibold">
                          ${Number(product.price).toFixed(2)}
                        </span>
                      </TableCell>,
                    ]
                  : []),
                ...(visibleColumns.category
                  ? [
                      <TableCell key="category">
                        {getCategoryName(product)}
                      </TableCell>,
                    ]
                  : []),
                ...(visibleColumns.status
                  ? [
                      <TableCell key="status">
                        <div className="flex flex-col gap-1">
                          <span
                            className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                              product.is_active
                                ? "bg-green-100 text-green-800"
                                : "bg-red-100 text-red-800"
                            }`}
                          >
                            {product.is_active ? "Active" : "Inactive"}
                          </span>
                          <span
                            className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getAvailabilityColor(
                              product.availability_type || "IN_STOCK",
                            )}`}
                          >
                            {(product.availability_type || "IN_STOCK").replace(
                              "_",
                              " ",
                            )}
                          </span>
                        </div>
                      </TableCell>,
                    ]
                  : []),
                ...(visibleColumns.actions
                  ? [
                      <TableCell key="actions">
                        <Button
                          color="danger"
                          size="sm"
                          variant="flat"
                          onClick={(e) => e.stopPropagation()}
                          onPress={() => handleDeleteProduct(product.id)}
                        >
                          Delete
                        </Button>
                      </TableCell>,
                    ]
                  : []),
              ]}
            </TableRow>
          ))}
        </TableBody>
      </Table>

      {/* Footer with Pagination */}
      <div className="px-6 py-4 border-t border-gray-200">
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-700">
            Showing {(currentPage - 1) * pageSize + 1} to{" "}
            {Math.min(currentPage * pageSize, totalCount)} of {totalCount}{" "}
            products
          </div>

          <div className="flex items-center gap-2">
            <Pagination
              showControls
              color="primary"
              page={currentPage}
              size="sm"
              total={totalPages}
              onChange={handlePageChange}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
