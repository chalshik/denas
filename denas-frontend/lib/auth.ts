import { auth } from './firebase';
import { onAuthStateChanged, User } from 'firebase/auth';

export interface UserRole {
  uid: string;
  role: 'admin' | 'user';
  email?: string;
}

// Check if user is admin
export const isAdmin = (): boolean => {
  if (typeof window === 'undefined') return false;
  return localStorage.getItem('userRole') === 'admin';
};

// Get current user role
export const getUserRole = (): 'admin' | 'user' | null => {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('userRole') as 'admin' | 'user' | null;
};

// Set user role (for demo purposes)
export const setUserRole = (role: 'admin' | 'user') => {
  if (typeof window === 'undefined') return;
  localStorage.setItem('userRole', role);
};

// Clear user role on logout
export const clearUserRole = () => {
  if (typeof window === 'undefined') return;
  localStorage.removeItem('userRole');
};

// Check if user is authenticated
export const isAuthenticated = (): boolean => {
  return auth.currentUser !== null;
};

// Get current user
export const getCurrentUser = (): User | null => {
  return auth.currentUser;
};

// Listen to auth state changes
export const onAuthStateChange = (callback: (user: User | null) => void) => {
  return onAuthStateChanged(auth, callback);
};

// Backend API base URL
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// Register user in backend
export async function registerUserBackend(idToken: string, phone: string) {
  const res = await fetch(`${API_BASE}/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${idToken}`,
    },
    body: JSON.stringify({ phone }),
  });
  if (!res.ok) throw new Error('Failed to register user in backend');
  return await res.json();
}

// Get current user profile (with role) from backend
export async function fetchUserProfile(idToken: string) {
  const res = await fetch(`${API_BASE}/auth/me`, {
    headers: {
      'Authorization': `Bearer ${idToken}`,
    },
  });
  if (!res.ok) throw new Error('Failed to fetch user profile');
  return await res.json();
}
