'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@heroui/button';
import { useModal } from '@/hooks/useModal';
import { useProducts } from '@/hooks/useProducts';
import { useCategories } from '@/hooks/useCategories';
import ProductsTable from '@/components/tables/ProductsTable';
import CreateProductModal from '@/components/modals/CreateProductModal';
import EditProductModal from '@/components/modals/EditProductModal';
import { Product } from '@/types';

export default function AdminProductsPage() {
  const { products = [], loading: loadingProducts, fetchProducts, createProduct, updateProduct, deleteProduct } = useProducts();
  const { categories = [], fetchCategories } = useCategories();
  const createModal = useModal();
  const editModal = useModal();
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);

  useEffect(() => {
    fetchProducts();
    fetchCategories();
  }, []);

  const handleCreateProduct = async (productData: any) => {
    await createProduct(productData);
    createModal.close();
  };

  const handleEditProduct = async (productData: any) => {
    if (selectedProduct) {
      await updateProduct(selectedProduct.id, productData);
      editModal.close();
      setSelectedProduct(null);
    }
  };

  const handleDeleteProduct = async (productId: number) => {
    if (confirm('Are you sure you want to delete this product?')) {
      await deleteProduct(productId);
    }
  };

  const handleEditClick = (product: Product) => {
    setSelectedProduct(product);
    editModal.open();
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
        onClose={createModal.close}
        onSubmit={handleCreateProduct}
        categories={categories}
        loading={loadingProducts}
      />

      <EditProductModal
        isOpen={editModal.isOpen}
        onClose={editModal.close}
        onSubmit={handleEditProduct}
        product={selectedProduct}
        categories={categories}
        loading={loadingProducts}
      />
    </div>
  );
}
