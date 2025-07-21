import { useApi } from "./useApi";
import { api } from "../lib/api";
import { Product, ProductCreate, ProductUpdate, ProductCatalog, ProductWithDetails, ProductListResponse, ProductFilters } from "../types";

export function useProducts() {
  const apiHook = useApi<ProductCatalog | ProductWithDetails>();

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
    apiHook.setLoading(true);
    try {
      // Use admin endpoint for complete product details (including inactive products)
      const products = await api.get<ProductWithDetails[]>("/products", { 
        skip: 0, 
        limit: 100, 
        include_inactive: true 
      });
      apiHook.setData(products);
    } catch (error: any) {
      apiHook.setError(error.message || "Failed to fetch products");
      throw error;
    } finally {
      apiHook.setLoading(false);
    }
  };

  const fetchAdminProducts = async (
    page: number = 1, 
    pageSize: number = 20, 
    includeInactive: boolean = true,
    filters: {
      categoryId?: number;
      minPrice?: number;
      maxPrice?: number;
      search?: string;
    } = {}
  ): Promise<{ products: ProductWithDetails[], total: number }> => {
    apiHook.setLoading(true);
    try {
      // If search is provided, use catalog endpoint (which supports search)
      if (filters.search && filters.search.trim()) {
        const searchParams: any = {
          page,
          size: pageSize,
          search: filters.search.trim(),
          is_active: includeInactive ? undefined : true, // catalog endpoint filters for active by default
        };

        // Add filter parameters for catalog endpoint
        if (filters.categoryId) {
          searchParams.category_id = filters.categoryId;
        }
        if (filters.minPrice !== undefined && filters.minPrice > 0) {
          searchParams.min_price = filters.minPrice;
        }
        if (filters.maxPrice !== undefined && filters.maxPrice > 0) {
          searchParams.max_price = filters.maxPrice;
        }

        const catalogResponse = await api.get<{
          items: ProductCatalog[];
          total: number;
          page: number;
          size: number;
          has_next: boolean;
          has_previous: boolean;
        }>("/products/catalog", searchParams);

        // Convert ProductCatalog to ProductWithDetails format for consistency
        const productsWithDetails: ProductWithDetails[] = catalogResponse.items.map((product: ProductCatalog) => ({
          id: product.id,
          name: product.name,
          description: '', // Catalog doesn't include description
          price: product.price,
          stock_quantity: 0, // Catalog doesn't include stock
          availability_type: product.availability_type || 'IN_STOCK',
          preorder_available_date: undefined,
          is_active: product.is_active,
          category_id: product.category_id,
          created_at: '', // Catalog doesn't include created_at
          updated_at: '',
          category: undefined, // Will be populated by categoryMap in component
          images: product.image_url ? [{ 
            id: 0, 
            product_id: product.id, 
            image_url: product.image_url, 
            image_type: 'official' as any,
            created_at: ''
          }] : [],
          favorites_count: 0
        }));

        return {
          products: productsWithDetails,
          total: catalogResponse.total
        };
      }

      // No search - use admin endpoint for full details
      const skip = (page - 1) * pageSize;
      const params: any = { 
        skip, 
        limit: pageSize, 
        include_inactive: includeInactive 
      };

      // Add filter parameters if provided
      if (filters.categoryId) {
        params.category_id = filters.categoryId;
      }
      if (filters.minPrice !== undefined && filters.minPrice > 0) {
        params.min_price = filters.minPrice;
      }
      if (filters.maxPrice !== undefined && filters.maxPrice > 0) {
        params.max_price = filters.maxPrice;
      }

      const response = await api.get<{
        items: ProductWithDetails[];
        total: number;
        page: number;
        size: number;
        has_next: boolean;
        has_previous: boolean;
      }>("/products", params);
      
      return { 
        products: response.items, 
        total: response.total 
      };
    } catch (error: any) {
      apiHook.setError(error.message || "Failed to fetch admin products");
      throw error;
    } finally {
      apiHook.setLoading(false);
    }
  };

  const fetchFeaturedProducts = async (limit: number = 10): Promise<ProductCatalog[]> => {
    apiHook.setLoading(true);
    try {
      const products = await api.get<ProductCatalog[]>("/products/featured", { limit });
      // Don't set the main data array for featured products, just return them
      return products;
    } catch (error: any) {
      apiHook.setError(error.message || "Failed to fetch featured products");
      throw error;
    } finally {
      apiHook.setLoading(false);
    }
  };

  const searchProducts = async (query: string, page: number = 1, size: number = 20): Promise<ProductListResponse> => {
    apiHook.setLoading(true);
    try {
      const response = await api.get<ProductListResponse>("/products/catalog", { 
        search: query, 
        page, 
        size 
      });
      apiHook.setData(response.items);
      return response;
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

  const updateProduct = async (id: number, productData: ProductUpdate): Promise<Product> => {
    apiHook.setLoading(true);
    try {
      let imageUrls: string[] = [];
      
      // If image_urls are provided directly (from EditProductModal), use them as-is
      if (productData.image_urls !== undefined) {
        imageUrls = productData.image_urls;
      } else {
        // Legacy: Upload images if File objects are provided
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
      }
      
      // Build update payload
      const productPayload: any = {};
      
      if (productData.name !== undefined) productPayload.name = productData.name;
      if (productData.description !== undefined) productPayload.description = productData.description;
      if (productData.price !== undefined) productPayload.price = productData.price;
      if (productData.category_id !== undefined) productPayload.category_id = productData.category_id;
      if (productData.stock_quantity !== undefined) productPayload.stock_quantity = productData.stock_quantity;
      if (productData.availability_type !== undefined) productPayload.availability_type = productData.availability_type;
      if (productData.preorder_available_date !== undefined) productPayload.preorder_available_date = productData.preorder_available_date;
      if (productData.is_active !== undefined) productPayload.is_active = productData.is_active;
      
      // Always include image_urls when provided (even if empty array for deletion)
      if (productData.image_urls !== undefined) {
        productPayload.image_urls = imageUrls;
      } else if (imageUrls.length > 0) {
        // Legacy: only add if there are uploaded images
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

  const getByCategory = async (categoryId: number, page: number = 1, size: number = 20): Promise<ProductListResponse> => {
    apiHook.setLoading(true);
    try {
      const response = await api.get<ProductListResponse>("/products/catalog", { 
        category_id: categoryId, 
        page, 
        size 
      });
      apiHook.setData(response.items);
      return response;
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
    fetchAdminProducts,
    fetchFeaturedProducts,
    searchProducts,
    getProductDetails,
    createProduct,
    updateProduct,
    deleteProduct,
    getByCategory,
  };
}