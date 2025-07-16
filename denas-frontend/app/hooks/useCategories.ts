import { useState } from 'react';
import { api } from '../../lib/api';
import { Category, CategoryCreate, CategoryWithProducts } from '../../types';

export function useCategories() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchCategories = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.get<Category[]>('/categories');
      setCategories(data);
      return data;
    } catch (error: any) {
      setError(error.message || "Failed to fetch categories");
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const createCategory = async (categoryData: CategoryCreate) => {
    setLoading(true);
    setError(null);
    try {
      const newCategory = await api.post<Category>('/categories', categoryData);
      setCategories(prev => [newCategory, ...prev]);
      return newCategory;
    } catch (error: any) {
      setError(error.message || "Failed to create category");
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const updateCategory = async (id: number, categoryData: Partial<CategoryCreate>) => {
    setLoading(true);
    setError(null);
    try {
      const updatedCategory = await api.put<Category>(`/categories/${id}`, categoryData);
      setCategories(prev => prev.map(category => 
        category.id === id ? updatedCategory : category
      ));
      return updatedCategory;
    } catch (error: any) {
      setError(error.message || "Failed to update category");
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const deleteCategory = async (id: number) => {
    setLoading(true);
    setError(null);
    try {
      await api.delete(`/categories/${id}`);
      setCategories(prev => prev.filter(category => category.id !== id));
    } catch (error: any) {
      setError(error.message || "Failed to delete category");
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const getWithProducts = async (id: number): Promise<CategoryWithProducts> => {
    setLoading(true);
    try {
      const category = await api.get<CategoryWithProducts>(`/categories/${id}/products`);
      return category;
    } catch (error: any) {
      setError(error.message || "Failed to fetch category with products");
      throw error;
    } finally {
      setLoading(false);
    }
  };

  return {
    categories,
    loading,
    error,
    fetchCategories,
    createCategory,
    updateCategory,
    deleteCategory,
    getWithProducts,
    setError,
  };
} 