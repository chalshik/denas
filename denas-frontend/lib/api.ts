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