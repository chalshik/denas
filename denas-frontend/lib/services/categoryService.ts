import { BaseService } from '../api';
import { Category, CategoryCreate, CategoryWithProducts } from '../../types';

class CategoryService extends BaseService {
  constructor() {
    super('/categories');
  }

  async getWithProducts(id: number): Promise<CategoryWithProducts> {
    const response = await fetch(`${this.baseUrl}/${id}/products`, {
      headers: await this.getHeaders(),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to fetch category with products: ${response.statusText}`);
    }
    
    return response.json();
  }
}

export const categoryService = new CategoryService();
export type { Category, CategoryCreate, CategoryWithProducts }; 