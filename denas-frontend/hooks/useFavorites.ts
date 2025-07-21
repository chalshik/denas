import { api } from "../lib/api";
import {
  FavoriteWithProduct,
  FavoriteCreate,
  FavoriteCheckResponse,
} from "../types";

import { useApi } from "./useApi";

export function useFavorites() {
  const apiHook = useApi<FavoriteWithProduct>();

  const fetchMyFavorites = async (
    skip: number = 0,
    limit: number = 100,
  ): Promise<FavoriteWithProduct[]> => {
    apiHook.setLoading(true);
    try {
      const favorites = await api.get<FavoriteWithProduct[]>(
        "/favorites/my-favorites",
        { skip, limit },
      );

      apiHook.setData(favorites);

      return favorites;
    } catch (error: any) {
      apiHook.setError(error.message || "Failed to fetch favorites");
      throw error;
    } finally {
      apiHook.setLoading(false);
    }
  };

  const addToFavorites = async (productId: number): Promise<void> => {
    try {
      const favoriteData: FavoriteCreate = { product_id: productId };

      await api.post("/favorites", favoriteData);

      // Don't refresh entire list - UI state is managed locally now
    } catch (error: any) {
      if (error.message?.includes("already in favorites")) {
        // Product already favorited - not really an error
        return;
      }
      apiHook.setError(error.message || "Failed to add to favorites");
      throw error;
    }
  };

  const removeFromFavorites = async (favoriteId: number): Promise<void> => {
    try {
      await api.delete(`/favorites/${favoriteId}`);

      // Don't refresh entire list - UI state is managed locally now
    } catch (error: any) {
      apiHook.setError(error.message || "Failed to remove from favorites");
      throw error;
    }
  };

  const removeFromFavoritesByProduct = async (
    productId: number,
  ): Promise<void> => {
    try {
      await api.delete(`/favorites/product/${productId}`);

      // Don't refresh entire list - UI state is managed locally now
    } catch (error: any) {
      apiHook.setError(error.message || "Failed to remove from favorites");
      throw error;
    }
  };

  const checkIsFavorited = async (
    productId: number,
  ): Promise<FavoriteCheckResponse> => {
    try {
      const response = await api.get<FavoriteCheckResponse>(
        `/favorites/product/${productId}/check`,
      );

      return response;
    } catch (error: any) {
      // If error, assume not favorited
      return {
        user_id: 0,
        product_id: productId,
        is_favorited: false,
        favorite_id: undefined,
      };
    }
  };

  const getFavoritesCount = async (productId: number): Promise<number> => {
    try {
      const response = await api.get<{
        product_id: number;
        favorites_count: number;
      }>(`/favorites/product/${productId}/count`);

      return response.favorites_count;
    } catch (error: any) {
      return 0;
    }
  };

  const toggleFavorite = async (productId: number): Promise<boolean> => {
    try {
      const checkResult = await checkIsFavorited(productId);

      if (checkResult.is_favorited && checkResult.favorite_id) {
        await removeFromFavorites(checkResult.favorite_id);

        return false; // Now not favorited
      } else {
        await addToFavorites(productId);

        return true; // Now favorited
      }
    } catch (error: any) {
      apiHook.setError(error.message || "Failed to toggle favorite");
      throw error;
    }
  };

  return {
    ...apiHook,
    favorites: apiHook.data || [],
    fetchMyFavorites,
    addToFavorites,
    removeFromFavorites,
    removeFromFavoritesByProduct,
    checkIsFavorited,
    getFavoritesCount,
    toggleFavorite,
  };
}
