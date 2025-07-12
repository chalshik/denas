import { auth } from './firebase';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export class ApiClient {
  private static async getAuthHeaders(): Promise<HeadersInit> {
    try {
      const user = auth.currentUser;
      if (!user) {
        return {};
      }
      
      const token = await user.getIdToken();
      return {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      };
    } catch (error) {
      console.error('Error getting auth headers:', error);
      return {
        'Content-Type': 'application/json',
      };
    }
  }

  private static async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers = await this.getAuthHeaders();
    
    const config: RequestInit = {
      ...options,
      headers: {
        ...headers,
        ...options.headers,
      },
    };

    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  // Auth endpoints
  static async registerUser(phone: string) {
    return this.makeRequest('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ phone }),
    });
  }

  static async getCurrentUser() {
    return this.makeRequest('/auth/me');
  }

  static async getOrCreateUser() {
    return this.makeRequest('/auth/me/or-create');
  }

  // Helper to get phone from current Firebase user
  static getCurrentUserPhone(): string | null {
    const user = auth.currentUser;
    if (!user || !user.email) return null;
    
    // Convert email back to phone number
    return user.email.replace('@phone.auth', '');
  }
}

export default ApiClient; 