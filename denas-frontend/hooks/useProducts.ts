import { useApi } from "./useApi";
import { api } from "../lib/api";
import { Product, ProductCreate } from "../types";

export function useProducts() {
  const apiHook = useApi<Product>();

  const fetchProducts = async (): Promise<void> => {
    apiHook.setLoading(true);
    try {
      const products = await api.get<Product[]>("/products");
      apiHook.setData(products);
    } catch (error: any) {
      apiHook.setError(error.message || "Failed to fetch products");
    } finally {
      apiHook.setLoading(false);
    }
  };

  const createProduct = async (productData: ProductCreate): Promise<Product> => {
    apiHook.setLoading(true);
    try {
      const product = await api.post<Product>("/products", productData);
      await fetchProducts(); // Refresh the list
      return product;
    } catch (error: any) {
      apiHook.setError(error.message || "Failed to create product");
      throw error;
    } finally {
      apiHook.setLoading(false);
    }
  };

  const updateProduct = async (id: number, productData: Partial<ProductCreate>): Promise<Product> => {
    apiHook.setLoading(true);
    try {
      const product = await api.put<Product>(`/products/${id}`, productData);
      await fetchProducts(); // Refresh the list
      return product;
    } catch (error: any) {
      apiHook.setError(error.message || "Failed to update product");
      throw error;
    } finally {
      apiHook.setLoading(false);
    }
  };

  const deleteProduct = async (id: number): Promise<void> => {
    apiHook.setLoading(true);
    try {
      await api.delete(`/products/${id}`);
      await fetchProducts(); // Refresh the list
    } catch (error: any) {
      apiHook.setError(error.message || "Failed to delete product");
      throw error;
    } finally {
      apiHook.setLoading(false);
    }
  };

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
    products: apiHook.data || [],
    fetchProducts,
    createProduct,
    updateProduct,
    deleteProduct,
    getByCategory,
  };
}