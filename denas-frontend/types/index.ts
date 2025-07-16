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
  image_url?: string;
  stock_quantity?: number;
  is_active?: boolean;
  availability_type?: string;
  preorder_available_date?: string;
  created_at?: string;
  updated_at?: string;
}

export interface CategoryWithProducts extends Category {
  products: Product[];
}

export interface ProductCreate {
  name: string;
  description?: string;
  price: number;
  category_id: number;
  image_url?: string;
  stock_quantity?: number;
}

export interface CategoryCreate {
  name: string;
  description?: string;
  image_url?: string;
}
