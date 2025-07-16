'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@heroui/button';
import { useModal } from '@/hooks/useModal';
import { useProducts } from '@/hooks/useProducts';
import ProductsTable from '@/components/tables/ProductsTable';
import CreateProductModal from '@/components/modals/CreateProductModal';
import EditProductModal from '@/components/modals/EditProductModal';
import { Product } from '@/types';

export default function AdminProductsPage() {
  const { products = [], loading: loadingProducts, fetchProducts, deleteProduct } = useProducts();
  const createModal = useModal();
  const editModal = useModal();
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);

  useEffect(() => {
    fetchProducts();
  }, []);

  const handleDeleteProduct = async (productId: number) => {
    if (confirm('Are you sure you want to delete this product?')) {
      await deleteProduct(productId);
    }
  };

  const handleEditClick = (product: Product) => {
    setSelectedProduct(product);
    editModal.open();
  };

  const handleCreateClose = () => {
    createModal.close();
    fetchProducts(); // Обновляем список после создания
  };

  const handleEditClose = () => {
    editModal.close();
    setSelectedProduct(null);
    fetchProducts(); // Обновляем список после редактирования
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Products Management</h1>
          <p className="text-gray-600 mt-2">Manage your product catalog</p>
        </div>
        <Button color="primary" onPress={createModal.open}>
          Add New Product
        </Button>
      </div>

      <ProductsTable
        products={products}
        loading={loadingProducts}
        onEdit={handleEditClick}
        onDelete={handleDeleteProduct}
      />

      <CreateProductModal
        isOpen={createModal.isOpen}
        onClose={handleCreateClose}
      />

      <EditProductModal
        isOpen={editModal.isOpen}
        onClose={handleEditClose}
        product={selectedProduct}
      />
    </div>
  );
}
