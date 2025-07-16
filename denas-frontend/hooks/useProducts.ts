import { useApi } from "./useApi";
import { api } from "../lib/api";
import { Product, ProductCreate } from "../types";

export function useProducts() {
  const apiHook = useApi<Product>();

  const getByCategory = async (categoryId: number): Promise<Product[]> => {
    apiHook.setLoading(true);
    try {
      const products = await api.get<Product[]>(`/products/category/${categoryId}`);
      return products;
    } catch (error: any) {
      apiHook.setError(error.message || "Failed to fetch products by category");
      throw error;
    } finally {
      apiHook.setLoading(false);
    }
  };

  return {
    ...apiHook,
    getByCategory,
  };
} 