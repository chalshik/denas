import { SVGProps } from "react";

export type IconSvgProps = SVGProps<SVGSVGElement> & {
  size?: number;
};

export interface Category {
  id: number;
  name: string;
  description?: string;
  image_url?: string;
  created_at?: string;
  updated_at?: string;
}

export enum AvailabilityType {
  IN_STOCK = "IN_STOCK",
  PRE_ORDER = "PRE_ORDER"
}

export interface Product {
  id: number;
  name: string;
  description?: string;
  price: number;
  category_id: number;
  category?: {
    id: number;
    name: string;
  };
  stock_quantity?: number;
  availability_type?: AvailabilityType;
  preorder_available_date?: string;
  is_active?: boolean;
  created_at?: string;
}

export interface ProductCatalog {
  id: number;
  name: string;
  price: number;
  image_url?: string;
  availability_type: AvailabilityType;
  is_active: boolean;
  category_id: number;
}

export interface ProductWithDetails extends Product {
  category?: Category;
  images: Array<{
    id: number;
    image_url: string;
    image_type: string;
    created_at: string;
  }>;
}

export interface ProductListResponse {
  items: ProductCatalog[];
  total: number;
  page: number;
  size: number;
  has_next: boolean;
  has_previous: boolean;
}

export interface ProductFilters {
  page?: number;
  size?: number;
  category_id?: number;
  min_price?: number;
  max_price?: number;
  availability_type?: AvailabilityType;
  is_active?: boolean;
  search?: string;
  sort_by?: string;
  sort_order?: string;
}

export interface CategoryWithProducts extends Category {
  products: Product[];
}

export interface ProductCreate {
  name: string;
  description?: string;
  price: number;
  category_id: number;
  image_urls?: string[];
  images?: File[]; // Для загрузки новых изображений
  stock_quantity?: number;
  availability_type?: AvailabilityType;
  preorder_available_date?: string;
  is_active?: boolean;
}

export interface ProductUpdate {
  name?: string;
  description?: string;
  price?: number;
  category_id?: number;
  image_urls?: string[];
  images?: File[]; // Для загрузки новых изображений
  stock_quantity?: number;
  availability_type?: AvailabilityType;
  preorder_available_date?: string;
  is_active?: boolean;
}

export interface CategoryCreate {
  name: string;
}
