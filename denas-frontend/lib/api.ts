import { auth } from './firebase';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// API Response Types
interface TokenResponse {
  success: boolean;
  message: string;
  expires_in?: number;
}

interface SessionResponse {
  success: boolean;
  user?: any;
  authenticated: boolean;
  message?: string;
}
// Backend API base URL
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// Get auth token from Firebase
const getAuthToken = async (): Promise<string | null> => {
  const { auth } = await import('./firebase');
  const { getIdToken } = await import('firebase/auth');
  
  if (!auth.currentUser) {
    return null;
  }
  
  try {
    return await getIdToken(auth.currentUser);
  } catch (error) {
    console.error('Failed to get auth token:', error);
    return null;
  }
};

// Universal API client
class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE) {
    this.baseUrl = baseUrl;
  }

  private async getHeaders(): Promise<HeadersInit> {
    const token = await getAuthToken();
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    return headers;
  }

  private async request<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = await this.getHeaders();
    
    const response = await fetch(url, {
      ...options,
      headers: {
        ...headers,
        ...options.headers,
      },
    });
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }
    
    return response.json();
  }

  // GET request
  async get<T>(endpoint: string, params?: Record<string, any>): Promise<T> {
    const url = new URL(`${this.baseUrl}${endpoint}`);
    
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          url.searchParams.append(key, String(value));
        }
      });
    }
    
    const headers = await this.getHeaders();
    const response = await fetch(url.toString(), { headers });
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }
    
    return response.json();
  }

  // Cookie-based request method
  private static async makeCookieRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const config: RequestInit = {
      ...options,
      credentials: 'include', // Include cookies in the request
      headers: {
        'Content-Type': 'application/json',
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

  // POST request
  async post<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  // PUT request
  async put<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  // PATCH request
  async patch<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  // DELETE request
  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'DELETE',
    });
  }

  static async getOrCreateUser() {
    return this.makeRequest('/auth/me/or-create');
  }

  // Cookie-based authentication methods
  static async setAuthCookies(idToken: string, refreshToken: string): Promise<TokenResponse> {
    return this.makeCookieRequest<TokenResponse>('/auth/set-cookie', {
      method: 'POST',
      body: JSON.stringify({
        id_token: idToken,
        refresh_token: refreshToken,
      }),
    });
  }

  static async refreshAuthToken(): Promise<TokenResponse> {
    return this.makeCookieRequest<TokenResponse>('/auth/refresh-token', {
      method: 'POST',
    });
  }

  static async checkSession(): Promise<SessionResponse> {
    return this.makeCookieRequest<SessionResponse>('/auth/session', {
      method: 'GET',
    });
  }

  static async logout(): Promise<TokenResponse> {
    return this.makeCookieRequest<TokenResponse>('/auth/logout', {
      method: 'POST',
    });
  }

  // Cookie-based current user method
  static async getCurrentUserFromCookie() {
    try {
      const sessionResponse = await this.checkSession();
      return sessionResponse.user;
    } catch (error) {
      console.error('Error getting user from cookie:', error);
      return null;
    }
  }

  // Helper to get phone from current Firebase user
  static getCurrentUserPhone(): string | null {
    const user = auth.currentUser;
    if (!user || !user.email) return null;
    
    // Convert email back to phone number
    return user.email.replace('@phone.auth', '');
  }

  // Utility method to handle token refresh automatically
  static async makeRequestWithAutoRefresh<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    try {
      return await this.makeCookieRequest<T>(endpoint, options);
    } catch (error) {
      if (error instanceof Error && error.message.includes('401')) {
        // Try to refresh token
        try {
          await this.refreshAuthToken();
          // Retry the original request
          return await this.makeCookieRequest<T>(endpoint, options);
        } catch (refreshError) {
          console.error('Token refresh failed:', refreshError);
          throw error;
        }
      }
      throw error;
    }
  }
}

export default ApiClient; 
  // Authentication methods
  async registerUser(phone: string): Promise<any> {
    return this.post('/auth/register', { phone });
  }

  async getCurrentUser(): Promise<any> {
    return this.get('/auth/me');
  }

  async getCurrentUserFromCookie(): Promise<any> {
    try {
      return await this.get('/auth/me-from-cookie');
    } catch {
      return null;
    }
  }

  async setAuthCookies(idToken: string, refreshToken: string): Promise<any> {
    return this.post('/auth/set-cookies', { idToken, refreshToken });
  }

  async logout(): Promise<any> {
    return this.post('/auth/logout');
  }

  async checkSession(): Promise<{ authenticated: boolean; user?: any }> {
    try {
      return await this.get('/auth/session');
    } catch {
      return { authenticated: false };
    }
  }

  async refreshAuthToken(): Promise<any> {
    return this.post('/auth/refresh');
  }

  // Upload methods
  async uploadFile(file: File, folder: string = 'uploads'): Promise<{success: boolean, file_url: string}> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('folder', folder);

    const token = await getAuthToken();
    const response = await fetch(`${API_BASE}/uploads/single`, {
      method: 'POST',
      headers: {
        'Authorization': token ? `Bearer ${token}` : '',
      },
      body: formData,
    });
    
    if (!response.ok) {
      throw new Error(`Failed to upload file: ${response.statusText}`);
    }
    
    return response.json();
  }

  async uploadMultipleFiles(files: File[], folder: string = 'uploads'): Promise<{success: boolean, files: Array<{file_url: string}>}> {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    formData.append('folder', folder);

    const token = await getAuthToken();
    const response = await fetch(`${API_BASE}/uploads/multiple`, {
      method: 'POST',
      headers: {
        'Authorization': token ? `Bearer ${token}` : '',
      },
      body: formData,
    });
    
    if (!response.ok) {
      throw new Error(`Failed to upload files: ${response.statusText}`);
    }
    
    return response.json();
  }

  async uploadProductImages(files: File[]): Promise<{success: boolean, image_urls: string[]}> {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));

    const token = await getAuthToken();
    const response = await fetch(`${API_BASE}/uploads/product-images`, {
      method: 'POST',
      headers: {
        'Authorization': token ? `Bearer ${token}` : '',
      },
      body: formData,
    });
    
    if (!response.ok) {
      throw new Error(`Failed to upload product images: ${response.statusText}`);
    }
    
    return response.json();
  }
}

// Create and export API instance
export const api = new ApiClient();

// Export the class as default for backward compatibility
export default ApiClient;

// Legacy BaseService for backward compatibility
export class BaseService {
  protected baseUrl: string;

  constructor(resourcePath: string) {
    this.baseUrl = `${API_BASE}${resourcePath}`;
  }

  protected async getHeaders(): Promise<HeadersInit> {
    const token = await getAuthToken();
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    return headers;
  }

  async list<T>(params?: { skip?: number; limit?: number; search?: string }): Promise<T[]> {
    const url = new URL(this.baseUrl);
    
    if (params?.skip) url.searchParams.append('skip', params.skip.toString());
    if (params?.limit) url.searchParams.append('limit', params.limit.toString());
    if (params?.search) url.searchParams.append('search', params.search);
    
    const response = await fetch(url.toString(), {
      headers: await this.getHeaders(),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to fetch list: ${response.statusText}`);
    }
    
    return response.json();
  }

  async getById<T>(id: number | string): Promise<T> {
    const response = await fetch(`${this.baseUrl}/${id}`, {
      headers: await this.getHeaders(),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to fetch item: ${response.statusText}`);
    }
    
    return response.json();
  }

  async create<T>(data: any): Promise<T> {
    const response = await fetch(this.baseUrl, {
      method: 'POST',
      headers: await this.getHeaders(),
      body: JSON.stringify(data),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to create item: ${response.statusText}`);
    }
    
    return response.json();
  }

  async update<T>(id: number | string, data: any): Promise<T> {
    const response = await fetch(`${this.baseUrl}/${id}`, {
      method: 'PUT',
      headers: await this.getHeaders(),
      body: JSON.stringify(data),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to update item: ${response.statusText}`);
    }
    
    return response.json();
  }

  async delete(id: number | string): Promise<void> {
    const response = await fetch(`${this.baseUrl}/${id}`, {
      method: 'DELETE',
      headers: await this.getHeaders(),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to delete item: ${response.statusText}`);
    }
  }

  async uploadFile(file: File, folder: string = 'uploads'): Promise<{success: boolean, file_url: string}> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('folder', folder);

    const token = await getAuthToken();
    const response = await fetch(`${API_BASE}/uploads/single`, {
      method: 'POST',
      headers: {
        'Authorization': token ? `Bearer ${token}` : '',
      },
      body: formData,
    });
    
    if (!response.ok) {
      throw new Error(`Failed to upload file: ${response.statusText}`);
    }
    
    return response.json();
  }

  async uploadMultipleFiles(files: File[], folder: string = 'uploads'): Promise<{success: boolean, files: Array<{file_url: string}>}> {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    formData.append('folder', folder);

    const token = await getAuthToken();
    const response = await fetch(`${API_BASE}/uploads/multiple`, {
      method: 'POST',
      headers: {
        'Authorization': token ? `Bearer ${token}` : '',
      },
      body: formData,
    });
    
    if (!response.ok) {
      throw new Error(`Failed to upload files: ${response.statusText}`);
    }
    
    return response.json();
  }
}