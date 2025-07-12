export enum AvailabilityType {
  IN_STOCK = 'in_stock',
  PRE_ORDER = 'pre_order',
  DISCONTINUED = 'discontinued'
}

export enum ImageType {
  OFFICIAL = 'official',
  RECEIVED = 'received',
  OTHER = 'other'
}

export interface Category {
  id: number;
  name: string;
  created_at: string;
}

export interface ProductImage {
  id: number;
  product_id: number;
  image_url: string;
  image_type: ImageType;
  created_at: string;
}

export interface ProductImageCreate {
  image_url: string;
  image_type: ImageType;
}

export interface ProductBase {
  name: string;
  description?: string | null;
  price: number;
  stock_quantity: number;
  availability_type: AvailabilityType;
  preorder_available_date?: string | null;
  is_active: boolean;
  category_id: number;
}

export interface ProductCreateRequest extends ProductBase {
  images: ProductImageCreate[];
}

export interface ProductUpdate {
  name?: string;
  description?: string | null;
  price?: number;
  stock_quantity?: number;
  availability_type?: AvailabilityType;
  preorder_available_date?: string | null;
  is_active?: boolean;
  category_id?: number;
}

export interface Product extends ProductBase {
  id: number;
  created_at: string;
}

export interface ProductCatalog {
  id: number;
  name: string;
  price: number;
  availability_type: AvailabilityType;
  is_active: boolean;
  category?: {
    id: number;
    name: string;
  } | null;
  primary_image?: {
    id: number;
    image_url: string;
    image_type: ImageType;
  } | null;
  favorites_count?: number;
}

export interface ProductDetailed extends Product {
  category?: Category | null;
  images: ProductImage[];
  favorites_count?: number;
}

export interface ProductStats {
  total_products: number;
  active_products: number;
  inactive_products: number;
  products_by_availability: {
    [AvailabilityType.IN_STOCK]: number;
    [AvailabilityType.PRE_ORDER]: number;
    [AvailabilityType.DISCONTINUED]: number;
  };
  products_by_category: {
    [key: string]: number;
  };
  low_stock_products: number;
  out_of_stock_products: number;
}

export interface ProductListResponse {
  products: ProductCatalog[];
  total_count: number;
  page: number;
  limit: number;
  has_next: boolean;
  has_previous: boolean;
} 