import { auth } from "./firebase";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

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

// Get auth token from Firebase
const getAuthToken = async (): Promise<string | null> => {
  const { auth } = await import("./firebase");
  const { getIdToken } = await import("firebase/auth");

  if (!auth.currentUser) {
    return null;
  }

  try {
    return await getIdToken(auth.currentUser);
  } catch (error) {
    return null;
  }
};

// Universal API client
class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async getHeaders(): Promise<HeadersInit> {
    const token = await getAuthToken();
    const headers: HeadersInit = {
      "Content-Type": "application/json",
    };

    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    return headers;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
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
      const errorData = await response.json().catch(() => ({}));

      throw new Error(
        errorData.detail ||
          `API Error: ${response.status} ${response.statusText}`,
      );
    }

    return response.json();
  }

  // Cookie-based request method (static for session management)
  private static async makeCookieRequest<T>(
    endpoint: string,
    options: RequestInit = {},
  ): Promise<T> {
    const config: RequestInit = {
      ...options,
      credentials: "include", // Include cookies in the request
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    };

    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));

      throw new Error(
        errorData.detail || `HTTP error! status: ${response.status}`,
      );
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
    const response = await fetch(url.toString(), {
      headers,
      credentials: "include",
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));

      throw new Error(
        errorData.detail ||
          `API Error: ${response.status} ${response.statusText}`,
      );
    }

    return response.json();
  }

  // POST request
  async post<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: "POST",
      body: data ? JSON.stringify(data) : undefined,
      credentials: "include",
    });
  }

  // PUT request
  async put<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: "PUT",
      body: data ? JSON.stringify(data) : undefined,
      credentials: "include",
    });
  }

  // PATCH request
  async patch<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: "PATCH",
      body: data ? JSON.stringify(data) : undefined,
      credentials: "include",
    });
  }

  // DELETE request
  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, {
      method: "DELETE",
      credentials: "include",
    });
  }

  // === Authentication Methods (Instance) ===

  // Register new user
  async registerUser(phone: string): Promise<any> {
    return this.post("/auth/register", { phone });
  }

  // Get current user (requires Firebase token)
  async getCurrentUser(): Promise<any> {
    return this.get("/auth/me");
  }

  // Get or create user
  async getOrCreateUser(): Promise<any> {
    return this.get("/auth/me/or-create");
  }

  // === Cookie-based Authentication Methods (Static) ===

  // Set authentication cookies after login
  static async setAuthCookies(
    idToken: string,
    refreshToken: string,
  ): Promise<TokenResponse> {
    return this.makeCookieRequest<TokenResponse>("/auth/set-cookie", {
      method: "POST",
      body: JSON.stringify({
        id_token: idToken,
        refresh_token: refreshToken,
      }),
    });
  }

  // Refresh authentication token using cookies
  static async refreshAuthToken(): Promise<TokenResponse> {
    return this.makeCookieRequest<TokenResponse>("/auth/refresh-token", {
      method: "POST",
    });
  }

  // Check current session
  static async checkSession(): Promise<SessionResponse> {
    return this.makeCookieRequest<SessionResponse>("/auth/session", {
      method: "GET",
    });
  }

  // Logout and clear cookies
  static async logout(): Promise<TokenResponse> {
    return this.makeCookieRequest<TokenResponse>("/auth/logout", {
      method: "POST",
    });
  }

  // Get current user from cookie session
  static async getCurrentUserFromCookie() {
    try {
      const sessionResponse = await this.checkSession();

      return sessionResponse.authenticated ? sessionResponse.user : null;
    } catch (error) {
      return null;
    }
  }

  // === Instance Method Wrappers for Authentication ===

  // Instance wrapper for setAuthCookies
  async setAuthCookies(
    idToken: string,
    refreshToken: string,
  ): Promise<TokenResponse> {
    return ApiClient.setAuthCookies(idToken, refreshToken);
  }

  // Instance wrapper for refreshAuthToken
  async refreshAuthToken(): Promise<TokenResponse> {
    return ApiClient.refreshAuthToken();
  }

  // Instance wrapper for checkSession
  async checkSession(): Promise<SessionResponse> {
    return ApiClient.checkSession();
  }

  // Instance wrapper for logout
  async logout(): Promise<TokenResponse> {
    return ApiClient.logout();
  }

  // Instance wrapper for getCurrentUserFromCookie
  async getCurrentUserFromCookie() {
    return ApiClient.getCurrentUserFromCookie();
  }

  // === Upload Methods ===

  async uploadFile(
    file: File,
    folder: string = "uploads",
  ): Promise<{ success: boolean; file_url: string }> {
    const formData = new FormData();

    formData.append("file", file);
    formData.append("folder", folder);

    const token = await getAuthToken();
    const response = await fetch(`${this.baseUrl}/uploads/single`, {
      method: "POST",
      headers: {
        Authorization: token ? `Bearer ${token}` : "",
      },
      body: formData,
      credentials: "include",
    });

    if (!response.ok) {
      throw new Error(`Failed to upload file: ${response.statusText}`);
    }

    return response.json();
  }

  async uploadMultipleFiles(
    files: File[],
    folder: string = "uploads",
  ): Promise<{ success: boolean; files: Array<{ file_url: string }> }> {
    const formData = new FormData();

    files.forEach((file) => formData.append("files", file));
    formData.append("folder", folder);

    const token = await getAuthToken();
    const response = await fetch(`${this.baseUrl}/uploads/multiple`, {
      method: "POST",
      headers: {
        Authorization: token ? `Bearer ${token}` : "",
      },
      body: formData,
      credentials: "include",
    });

    if (!response.ok) {
      throw new Error(`Failed to upload files: ${response.statusText}`);
    }

    return response.json();
  }

  async uploadProductImages(
    files: File[],
  ): Promise<{ success: boolean; image_urls: string[] }> {
    const formData = new FormData();

    files.forEach((file) => formData.append("files", file));

    const token = await getAuthToken();
    const response = await fetch(`${this.baseUrl}/uploads/product-images`, {
      method: "POST",
      headers: {
        Authorization: token ? `Bearer ${token}` : "",
      },
      body: formData,
      credentials: "include",
    });

    if (!response.ok) {
      throw new Error(
        `Failed to upload product images: ${response.statusText}`,
      );
    }

    return response.json();
  }

  // === Utility Methods ===

  // Helper to get phone from current Firebase user
  static getCurrentUserPhone(): string | null {
    const user = auth.currentUser;

    if (!user || !user.email) return null;

    // Convert email back to phone number
    return user.email.replace("@phone.auth", "");
  }

  // Utility method to handle token refresh automatically
  static async makeRequestWithAutoRefresh<T>(
    endpoint: string,
    options: RequestInit = {},
  ): Promise<T> {
    try {
      return await this.makeCookieRequest<T>(endpoint, options);
    } catch (error) {
      if (error instanceof Error && error.message.includes("401")) {
        // Try to refresh token
        try {
          await this.refreshAuthToken();

          // Retry the original request
          return await this.makeCookieRequest<T>(endpoint, options);
        } catch (refreshError) {
          throw error;
        }
      }
      throw error;
    }
  }
}

// Create and export API instance
export const api = new ApiClient();

// Export the class as well
export { ApiClient };

// Export default
export default ApiClient;
