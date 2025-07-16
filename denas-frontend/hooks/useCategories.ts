import { useApi } from "./useApi";
import { api } from "../lib/api";
import { Category, CategoryCreate, CategoryWithProducts } from "../types";

export function useCategories() {
  const apiHook = useApi<Category>();

  const fetchCategories = async (): Promise<void> => {
    apiHook.setLoading(true);
    try {
      const categories = await api.get<Category[]>("/categories");
      apiHook.setData(categories);
    } catch (error: any) {
      apiHook.setError(error.message || "Failed to fetch categories");
    } finally {
      apiHook.setLoading(false);
    }
  };

  const getWithProducts = async (id: number): Promise<CategoryWithProducts> => {
    apiHook.setLoading(true);
    try {
      const category = await api.get<CategoryWithProducts>(`/categories/${id}/products`);
      return category;
    } catch (error: any) {
      apiHook.setError(error.message || "Failed to fetch category with products");
      throw error;
    } finally {
      apiHook.setLoading(false);
    }
  };

  return {
    ...apiHook,
    categories: apiHook.data || [],
    fetchCategories,
    getWithProducts,
  };
}