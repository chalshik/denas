import { api } from "../api";
import { Product, ProductCreate } from "../../types";

class ProductService {
  private basePath = "/products";

  async list(): Promise<Product[]> {
    return api.get<Product[]>(this.basePath);
  }

  async getById(id: number): Promise<Product> {
    return api.get<Product>(`${this.basePath}/${id}`);
  }

  async create(data: ProductCreate): Promise<Product> {
    return api.post<Product>(this.basePath, data);
  }

  async update(id: number, data: Partial<ProductCreate>): Promise<Product> {
    return api.put<Product>(`${this.basePath}/${id}`, data);
  }

  async delete(id: number): Promise<void> {
    return api.delete<void>(`${this.basePath}/${id}`);
  }

  async getByCategory(categoryId: number): Promise<Product[]> {
    return api.get<Product[]>(`${this.basePath}/category/${categoryId}`);
  }
}

export const productService = new ProductService();
export type { Product, ProductCreate };
