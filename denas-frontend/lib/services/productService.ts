import { BaseService } from '../api';
import { Product, ProductCreate } from '../../types';

class ProductService extends BaseService {
  constructor() {
    super('/products');
  }

  async getByCategory(categoryId: number): Promise<Product[]> {
    const response = await fetch(`${this.baseUrl}/category/${categoryId}`, {
      headers: await this.getHeaders(),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to fetch products by category: ${response.statusText}`);
    }
    
    return response.json();
  }
}

export const productService = new ProductService();
export type { Product, ProductCreate }; 