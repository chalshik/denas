import { useApi } from "./useApi";
import { api } from "../lib/api";
import { Product, ProductCreate, ProductCatalog, ProductWithDetails, ProductListResponse, ProductFilters } from "../types";

export function useProducts() {
  const apiHook = useApi<ProductCatalog>();

  const fetchProductsCatalog = async (filters: ProductFilters = {}): Promise<ProductListResponse> => {
    apiHook.setLoading(true);
    try {
      const response = await api.get<ProductListResponse>("/products/catalog", filters);
      apiHook.setData(response.items);
      return response;
    } catch (error: any) {
      apiHook.setError(error.message || "Failed to fetch products catalog");
      throw error;
    } finally {
      apiHook.setLoading(false);
    }
  };

  const fetchProducts = async (): Promise<void> => {
    const response = await fetchProductsCatalog({ page: 1, size: 100 });
    // Data is already set in fetchProductsCatalog
  };

  const fetchFeaturedProducts = async (limit: number = 10): Promise<ProductCatalog[]> => {
    apiHook.setLoading(true);
    try {
      const products = await api.get<ProductCatalog[]>("/products/featured", { limit });
      return products;
    } catch (error: any) {
      apiHook.setError(error.message || "Failed to fetch featured products");
      throw error;
    } finally {
      apiHook.setLoading(false);
    }
  };

  const searchProducts = async (query: string, skip: number = 0, limit: number = 20): Promise<ProductCatalog[]> => {
    apiHook.setLoading(true);
    try {
      const products = await api.get<ProductCatalog[]>("/products/search", { q: query, skip, limit });
      return products;
    } catch (error: any) {
      apiHook.setError(error.message || "Failed to search products");
      throw error;
    } finally {
      apiHook.setLoading(false);
    }
  };

  const getProductDetails = async (id: number): Promise<ProductWithDetails> => {
    apiHook.setLoading(true);
    try {
      const product = await api.get<ProductWithDetails>(`/products/${id}`);
      return product;
    } catch (error: any) {
      apiHook.setError(error.message || "Failed to fetch product details");
      throw error;
    } finally {
      apiHook.setLoading(false);
    }
  };

  const createProduct = async (productData: ProductCreate): Promise<Product> => {
    apiHook.setLoading(true);
    try {
      let imageUrls: string[] = [];
      
      // Загружаем изображения если они есть
      if (productData.images && productData.images.length > 0) {
        const uploadResponse = await api.uploadProductImages(productData.images);
        imageUrls = uploadResponse.image_urls;
      }
      
      // Создаем продукт с URL изображений
      const productPayload = {
        ...productData,
        image_urls: imageUrls
      };
      
      // Удаляем файлы из payload, так как они больше не нужны
      delete (productPayload as any).images;
      
      const product = await api.post<Product>("/products", productPayload);
      
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
      let imageUrls: string[] = [];
      
      // Загружаем изображения если они есть
      if (productData.images && productData.images.length > 0) {
        const uploadResponse = await api.uploadProductImages(productData.images);
        imageUrls = uploadResponse.image_urls;
      }
      
      // Обновляем продукт с URL изображений
      const productPayload = {
        ...productData,
        image_urls: imageUrls.length > 0 ? imageUrls : productData.image_urls
      };
      
      // Удаляем файлы из payload, так как они больше не нужны
      delete (productPayload as any).images;
      
      const product = await api.put<Product>(`/products/${id}`, productPayload);
      
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

  const getByCategory = async (categoryId: number, skip: number = 0, limit: number = 20): Promise<ProductCatalog[]> => {
    apiHook.setLoading(true);
    try {
      const products = await api.get<ProductCatalog[]>(`/products/category/${categoryId}`, { skip, limit });
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
    fetchProductsCatalog,
    fetchFeaturedProducts,
    searchProducts,
    getProductDetails,
    createProduct,
    updateProduct,
    deleteProduct,
    getByCategory,
  };
}