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
        try {
          const uploadResponse = await api.uploadProductImages(productData.images);
          imageUrls = uploadResponse.image_urls;
        } catch (uploadError: any) {
          // If product image upload fails due to permissions, try regular upload
          if (uploadError.message?.includes('Forbidden') || uploadError.message?.includes('403')) {
            console.warn('Product image upload failed, trying regular upload...');
            const regularUploadResponse = await api.uploadMultipleFiles(productData.images, 'product-images');
            imageUrls = regularUploadResponse.files.map(f => f.file_url);
          } else {
            throw uploadError;
          }
        }
      }
      
      // Если есть уже готовые URL изображений, добавляем их
      if (productData.image_urls && productData.image_urls.length > 0) {
        imageUrls = [...imageUrls, ...productData.image_urls];
      }
      
      // Создаем продукт с правильной структурой данных для бэкенда
      const productPayload = {
        name: productData.name,
        description: productData.description,
        price: productData.price,
        category_id: productData.category_id,
        stock_quantity: productData.stock_quantity || 0,
        availability_type: productData.availability_type || 'IN_STOCK',
        preorder_available_date: productData.preorder_available_date || null,
        is_active: productData.is_active !== undefined ? productData.is_active : true,
        image_urls: imageUrls
      };
      
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
        try {
          const uploadResponse = await api.uploadProductImages(productData.images);
          imageUrls = uploadResponse.image_urls;
        } catch (uploadError: any) {
          // If product image upload fails due to permissions, try regular upload
          if (uploadError.message?.includes('Forbidden') || uploadError.message?.includes('403')) {
            console.warn('Product image upload failed, trying regular upload...');
            const regularUploadResponse = await api.uploadMultipleFiles(productData.images, 'product-images');
            imageUrls = regularUploadResponse.files.map(f => f.file_url);
          } else {
            throw uploadError;
          }
        }
      }
      
      // Если есть уже готовые URL изображений, используем их
      if (productData.image_urls && productData.image_urls.length > 0) {
        imageUrls = [...imageUrls, ...productData.image_urls];
      }
      
      // Обновляем продукт с правильной структурой данных
      const productPayload: any = {};
      
      if (productData.name !== undefined) productPayload.name = productData.name;
      if (productData.description !== undefined) productPayload.description = productData.description;
      if (productData.price !== undefined) productPayload.price = productData.price;
      if (productData.category_id !== undefined) productPayload.category_id = productData.category_id;
      if (productData.stock_quantity !== undefined) productPayload.stock_quantity = productData.stock_quantity;
      if (productData.availability_type !== undefined) productPayload.availability_type = productData.availability_type;
      if (productData.preorder_available_date !== undefined) productPayload.preorder_available_date = productData.preorder_available_date;
      if (productData.is_active !== undefined) productPayload.is_active = productData.is_active;
      
      // Добавляем image_urls только если есть новые изображения
      if (imageUrls.length > 0) {
        productPayload.image_urls = imageUrls;
      }
      
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