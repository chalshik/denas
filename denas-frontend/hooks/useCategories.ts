import { api } from "../lib/api";
import {
  Category,
  CategoryCreate,
  CategoryWithProducts,
  CategoryWithMetadata,
} from "../types";

import { useApi } from "./useApi";

export function useCategories() {
  const apiHook = useApi<Category>();

  const fetchCategories = async (
    skip: number = 0,
    limit: number = 100,
  ): Promise<void> => {
    apiHook.setLoading(true);
    try {
      const categories = await api.get<Category[]>("/categories", {
        skip,
        limit,
      });

      apiHook.setData(categories);
    } catch (error: any) {
      apiHook.setError(error.message || "Failed to fetch categories");
    } finally {
      apiHook.setLoading(false);
    }
  };

  const fetchCategoriesWithMetadata = async (
    skip: number = 0,
    limit: number = 100,
  ): Promise<CategoryWithMetadata[]> => {
    apiHook.setLoading(true);
    try {
      const categories = await api.get<CategoryWithMetadata[]>(
        "/categories/admin/with-metadata",
        { skip, limit },
      );

      return categories;
    } catch (error: any) {
      apiHook.setError(
        error.message || "Failed to fetch categories with metadata",
      );
      throw error;
    } finally {
      apiHook.setLoading(false);
    }
  };

  const getCategoryById = async (id: number): Promise<Category> => {
    apiHook.setLoading(true);
    try {
      const category = await api.get<Category>(`/categories/${id}`);

      return category;
    } catch (error: any) {
      apiHook.setError(error.message || "Failed to fetch category");
      throw error;
    } finally {
      apiHook.setLoading(false);
    }
  };

  const getWithProducts = async (id: number): Promise<CategoryWithProducts> => {
    apiHook.setLoading(true);
    try {
      const category = await api.get<CategoryWithProducts>(
        `/categories/${id}/with-products`,
      );

      return category;
    } catch (error: any) {
      apiHook.setError(
        error.message || "Failed to fetch category with products",
      );
      throw error;
    } finally {
      apiHook.setLoading(false);
    }
  };

  const searchCategories = async (
    searchTerm: string,
    skip: number = 0,
    limit: number = 100,
  ): Promise<Category[]> => {
    apiHook.setLoading(true);
    try {
      const categories = await api.get<Category[]>(
        `/categories/search/${searchTerm}`,
        { skip, limit },
      );

      return categories;
    } catch (error: any) {
      apiHook.setError(error.message || "Failed to search categories");
      throw error;
    } finally {
      apiHook.setLoading(false);
    }
  };

  const createCategory = async (
    categoryData: CategoryCreate,
  ): Promise<Category> => {
    apiHook.setLoading(true);
    try {
      const category = await api.post<Category>("/categories", categoryData);

      await fetchCategories(); // Refresh the list

      return category;
    } catch (error: any) {
      apiHook.setError(error.message || "Failed to create category");
      throw error;
    } finally {
      apiHook.setLoading(false);
    }
  };

  const updateCategory = async (
    id: number,
    categoryData: Partial<CategoryCreate>,
  ): Promise<Category> => {
    apiHook.setLoading(true);
    try {
      const category = await api.put<Category>(
        `/categories/${id}`,
        categoryData,
      );

      await fetchCategories(); // Refresh the list

      return category;
    } catch (error: any) {
      apiHook.setError(error.message || "Failed to update category");
      throw error;
    } finally {
      apiHook.setLoading(false);
    }
  };

  const deleteCategory = async (id: number): Promise<void> => {
    apiHook.setLoading(true);
    try {
      await api.delete(`/categories/${id}`);
      await fetchCategories(); // Refresh the list
    } catch (error: any) {
      apiHook.setError(error.message || "Failed to delete category");
      throw error;
    } finally {
      apiHook.setLoading(false);
    }
  };

  return {
    ...apiHook,
    categories: apiHook.data || [],
    fetchCategories,
    fetchCategoriesWithMetadata,
    getCategoryById,
    getWithProducts,
    searchCategories,
    createCategory,
    updateCategory,
    deleteCategory,
  };
}
