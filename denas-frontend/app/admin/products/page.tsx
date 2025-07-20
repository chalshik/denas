'use client';

import React, { useState } from 'react';
import { Button } from '@heroui/button';
import { useModal } from '@/hooks/useModal';
import { useProducts } from '@/hooks/useProducts';
import ProductsTable from '@/components/tables/ProductsTable';
import CreateProductModal from '@/components/modals/CreateProductModal';
import ProductDetailsModal from '@/components/modals/ProductDetailsModal';
import { Product } from '@/types';

export default function AdminProductsPage() {
  const { deleteProduct } = useProducts();
  const createModal = useModal();
  const detailsModal = useModal();
  const [selectedProductId, setSelectedProductId] = useState<number | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const handleDeleteProduct = async (productId: number) => {
    if (confirm('Are you sure you want to delete this product?')) {
      await deleteProduct(productId);
      // Trigger refresh after successful delete
      setRefreshKey(prev => prev + 1);
    }
  };

  const handleViewDetails = (product: Product) => {
    setSelectedProductId(product.id);
    detailsModal.open();
  };

  // Only refresh after successful operations, not on modal close
  const handleSuccess = () => {
    setRefreshKey(prev => prev + 1);
  };

  const handleCreateClose = () => {
    createModal.close();
  };

  const handleDetailsClose = () => {
    detailsModal.close();
    setSelectedProductId(null);
  };

  const handleDataChange = () => {
    // This is called when ProductsTable wants to notify of data changes
    setRefreshKey(prev => prev + 1);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Products Management</h1>
          <p className="text-gray-600 mt-2">Manage your product catalog</p>
        </div>
        <Button 
          color="primary" 
          size="lg"
          onPress={createModal.open}
        >
          Add New Product
        </Button>
      </div>

      <ProductsTable
        key={refreshKey} // Force refresh when key changes
        onDelete={handleDeleteProduct}
        onViewDetails={handleViewDetails}
        onDataChange={handleDataChange}
      />

      {/* Create Product Modal */}
      <CreateProductModal
        isOpen={createModal.isOpen}
        onClose={handleCreateClose}
        onSuccess={handleSuccess}
      />

      {/* Product Details Modal */}
      <ProductDetailsModal
        isOpen={detailsModal.isOpen}
        onClose={handleDetailsClose}
        onSuccess={handleSuccess}
        productId={selectedProductId}
      />
    </div>
  );
}
