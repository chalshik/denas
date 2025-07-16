import { useApi } from "./useApi";
import { api } from "../lib/api";
import { Category, CategoryCreate, CategoryWithProducts } from "../types";

export function useCategories() {
  const apiHook = useApi<Category>();

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
    getWithProducts,
  };
} 