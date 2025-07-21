import { api } from "../api";
import { Category, CategoryCreate, CategoryWithProducts } from "../../types";

class CategoryService {
  private basePath = "/categories";

  async list(): Promise<Category[]> {
    return api.get<Category[]>(this.basePath);
  }

  async getById(id: number): Promise<Category> {
    return api.get<Category>(`${this.basePath}/${id}`);
  }

  async create(data: CategoryCreate): Promise<Category> {
    return api.post<Category>(this.basePath, data);
  }

  async update(id: number, data: Partial<CategoryCreate>): Promise<Category> {
    return api.put<Category>(`${this.basePath}/${id}`, data);
  }

  async delete(id: number): Promise<void> {
    return api.delete<void>(`${this.basePath}/${id}`);
  }

  async getWithProducts(id: number): Promise<CategoryWithProducts> {
    return api.get<CategoryWithProducts>(`${this.basePath}/${id}/products`);
  }
}

export const categoryService = new CategoryService();
export type { Category, CategoryCreate, CategoryWithProducts };
