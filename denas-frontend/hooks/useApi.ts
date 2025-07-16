import { useState } from "react";
import { api } from "../lib/api";

interface UseApiState<T> {
  data: T[];
  item: T | null;
  loading: boolean;
  error: string | null;
}

export function useApi<T>() {
  const [state, setState] = useState<UseApiState<T>>({
    data: [],
    item: null,
    loading: false,
    error: null,
  });

  const setLoading = (loading: boolean) => {
    setState(prev => ({ ...prev, loading }));
  };

  const setError = (error: string | null) => {
    setState(prev => ({ ...prev, error }));
  };

  // Fetch list
  const fetchList = async (endpoint: string, params?: Record<string, any>) => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await api.get<T[]>(endpoint, params);
      setState(prev => ({ ...prev, data, loading: false }));
      return data;
    } catch (error: any) {
      setError(error.message || "Failed to fetch data");
      setLoading(false);
      throw error;
    }
  };

  // Fetch single item
  const fetchItem = async (endpoint: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const item = await api.get<T>(endpoint);
      setState(prev => ({ ...prev, item, loading: false }));
      return item;
    } catch (error: any) {
      setError(error.message || "Failed to fetch item");
      setLoading(false);
      throw error;
    }
  };

  // Create item
  const createItem = async (endpoint: string, data: any) => {
    setLoading(true);
    setError(null);
    
    try {
      const newItem = await api.post<T>(endpoint, data);
      setState(prev => ({ 
        ...prev, 
        data: [newItem, ...prev.data],
        loading: false 
      }));
      return newItem;
    } catch (error: any) {
      setError(error.message || "Failed to create item");
      setLoading(false);
      throw error;
    }
  };

  // Update item
  const updateItem = async (endpoint: string, data: any) => {
    setLoading(true);
    setError(null);
    
    try {
      const updatedItem = await api.put<T>(endpoint, data);
      setState(prev => ({
        ...prev,
        data: prev.data.map((item: any) => 
          (item as any).id === (updatedItem as any).id ? updatedItem : item
        ),
        item: prev.item && (prev.item as any).id === (updatedItem as any).id ? updatedItem : prev.item,
        loading: false
      }));
      return updatedItem;
    } catch (error: any) {
      setError(error.message || "Failed to update item");
      setLoading(false);
      throw error;
    }
  };

  // Patch item
  const patchItem = async (endpoint: string, data: any) => {
    setLoading(true);
    setError(null);
    
    try {
      const updatedItem = await api.patch<T>(endpoint, data);
      setState(prev => ({
        ...prev,
        data: prev.data.map((item: any) => 
          (item as any).id === (updatedItem as any).id ? updatedItem : item
        ),
        item: prev.item && (prev.item as any).id === (updatedItem as any).id ? updatedItem : prev.item,
        loading: false
      }));
      return updatedItem;
    } catch (error: any) {
      setError(error.message || "Failed to patch item");
      setLoading(false);
      throw error;
    }
  };

  // Delete item
  const deleteItem = async (endpoint: string) => {
    setLoading(true);
    setError(null);
    
    try {
      await api.delete(endpoint);
      // Extract ID from endpoint for state update
      const id = endpoint.split('/').pop();
      setState(prev => ({
        ...prev,
        data: prev.data.filter((item: any) => item.id !== id),
        item: prev.item && (prev.item as any).id !== id ? prev.item : null,
        loading: false
      }));
    } catch (error: any) {
      setError(error.message || "Failed to delete item");
      setLoading(false);
      throw error;
    }
  };

  return {
    ...state,
    fetchList,
    fetchItem,
    createItem,
    updateItem,
    patchItem,
    deleteItem,
    setError,
    setLoading,
  };
} 