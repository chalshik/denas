import { useState } from 'react';
import { api } from '../../lib/api';
import { Product, ProductCreate } from '../../types';

export function useProductsAdmin() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchProducts = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.get<Product[]>('/products');
      setProducts(data);
      return data;
    } catch (error: any) {
      setError(error.message || "Failed to fetch products");
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const createProduct = async (productData: any) => {
    setLoading(true);
    setError(null);
    try {
      // Handle image upload first
      const image_urls = await handleUploadImages(productData.images);
      
      const payload = {
        ...productData,
        price: Number(productData.price),
        stock_quantity: Number(productData.stock_quantity),
        category_id: Number(productData.category_id),
        images: image_urls.map((url: string) => ({ url })),
      };

      const newProduct = await api.post<Product>('/products', payload);
      setProducts(prev => [newProduct, ...prev]);
      return newProduct;
    } catch (error: any) {
      setError(error.message || "Failed to create product");
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const updateProduct = async (id: number, productData: any) => {
    setLoading(true);
    setError(null);
    try {
      // Handle image upload if new images are provided
      let image_urls: string[] = [];
      if (productData.images && productData.images.length > 0) {
        image_urls = await handleUploadImages(productData.images);
      }

      const payload = {
        ...productData,
        price: Number(productData.price),
        stock_quantity: Number(productData.stock_quantity),
        category_id: Number(productData.category_id),
        ...(image_urls.length > 0 && { images: image_urls.map((url: string) => ({ url })) }),
      };

      const updatedProduct = await api.put<Product>(`/products/${id}`, payload);
      setProducts(prev => prev.map(product => 
        product.id === id ? updatedProduct : product
      ));
      return updatedProduct;
    } catch (error: any) {
      setError(error.message || "Failed to update product");
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const deleteProduct = async (id: number) => {
    setLoading(true);
    setError(null);
    try {
      await api.delete(`/products/${id}`);
      setProducts(prev => prev.filter(product => product.id !== id));
    } catch (error: any) {
      setError(error.message || "Failed to delete product");
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const getByCategory = async (categoryId: number): Promise<Product[]> => {
    setLoading(true);
    try {
      const products = await api.get<Product[]>(`/products/category/${categoryId}`);
      return products;
    } catch (error: any) {
      setError(error.message || "Failed to fetch products by category");
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const handleUploadImages = async (images: File[]): Promise<string[]> => {
    if (!images.length) return [];
    
    const formData = new FormData();
    images.forEach(file => formData.append('files', file));
    
    const response = await api.post<{ image_urls: string[] }>('/uploads/product-images', formData);
    return response.image_urls || [];
  };

  return {
    products,
    loading,
    error,
    fetchProducts,
    createProduct,
    updateProduct,
    deleteProduct,
    getByCategory,
    setError,
  };
} 