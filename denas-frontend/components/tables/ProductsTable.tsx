'use client';

import React, { useState } from 'react';
import { Button } from '@heroui/button';
import { Input } from '@heroui/input';
import { Table, TableHeader, TableColumn, TableBody, TableRow, TableCell } from '@heroui/table';
import { Image } from '@heroui/image';
import { Product, ProductCatalog } from '@/types';

interface ProductsTableProps {
  products: (Product | ProductCatalog)[];
  loading: boolean;
  onEdit: (product: Product | ProductCatalog) => void;
  onDelete: (productId: number) => void;
  onViewDetails?: (product: Product | ProductCatalog) => void;
}

export default function ProductsTable({ 
  products, 
  loading, 
  onEdit, 
  onDelete, 
  onViewDetails 
}: ProductsTableProps) {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredProducts = products.filter(product =>
    (product.name?.toLowerCase() || '').includes(searchTerm.toLowerCase()) ||
    (('category' in product && product.category?.name || '').toLowerCase().includes(searchTerm.toLowerCase()))
  );

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
      case 'DISCONTINUED':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="p-6 border-b border-gray-200">
        <div className="flex justify-between items-center">
          <h3 className="text-lg font-semibold text-gray-900">Products</h3>
          <Input
            placeholder="Search products..."
            value={searchTerm}
            onValueChange={setSearchTerm}
            className="max-w-md"
            variant="bordered"
            classNames={{
              input: "text-gray-900",
              inputWrapper: "border-gray-300"
            }}
          />
        </div>
      </div>

      <Table 
        aria-label="Products table"
        classNames={{
          base: "bg-white",
          wrapper: "bg-white shadow-none",
          th: "bg-gray-50 text-gray-700 font-medium",
          td: "text-gray-900 border-b border-gray-100",
          tbody: "bg-white"
        }}
      >
        <TableHeader>
          <TableColumn>Image</TableColumn>
          <TableColumn>Name</TableColumn>
          <TableColumn>Price</TableColumn>
          <TableColumn>Category</TableColumn>
          <TableColumn>Stock</TableColumn>
          <TableColumn>Status</TableColumn>
          <TableColumn>Availability</TableColumn>
          <TableColumn>Actions</TableColumn>
        </TableHeader>
        <TableBody 
          emptyContent={loading ? "Loading products..." : "No products found"}
          isLoading={loading}
        >
          {filteredProducts.map((product) => (
            <TableRow key={product.id}>
              <TableCell>
                <div className="w-16 h-16 rounded-lg overflow-hidden bg-gray-100">
                  {'image_url' in product && product.image_url ? (
                    <Image
                      src={product.image_url}
                      alt={product.name}
                      className="w-full h-full object-cover"
                      fallbackSrc="/placeholder-product.png"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-gray-400">
                      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                    </div>
                  )}
                </div>
              </TableCell>
              <TableCell>
                <div className="font-medium text-gray-900">{product.name}</div>
              </TableCell>
              <TableCell>
                <span className="font-semibold text-gray-900">
                  {formatPrice(product.price)}
                </span>
              </TableCell>
              <TableCell>
                <span className="text-gray-600">
                  {'category' in product && product.category?.name ? product.category.name : `Category ${product.category_id}`}
                </span>
              </TableCell>
              <TableCell>
                <span className="text-gray-600">
                  {'stock_quantity' in product ? product.stock_quantity || 0 : 'N/A'}
                </span>
              </TableCell>
              <TableCell>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  product.is_active ? 'text-green-600 bg-green-100' : 'text-red-600 bg-red-100'
                }`}>
                  {product.is_active ? 'Active' : 'Inactive'}
                </span>
              </TableCell>
              <TableCell>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  getAvailabilityColor(product.availability_type || 'IN_STOCK')
                }`}>
                  {(product.availability_type || 'IN_STOCK').replace('_', ' ')}
                </span>
              </TableCell>
              <TableCell>
                <div className="flex gap-2">
                  {onViewDetails && (
                    <Button
                      size="sm"
                      variant="flat"
                      color="primary"
                      onPress={() => onViewDetails(product)}
                    >
                      View
                    </Button>
                  )}
                  <Button
                    size="sm"
                    variant="flat"
                    color="warning"
                    onPress={() => onEdit(product)}
                  >
                    Edit
                  </Button>
                  <Button
                    size="sm"
                    variant="flat"
                    color="danger"
                    onPress={() => onDelete(product.id)}
                  >
                    Delete
                  </Button>
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
} 