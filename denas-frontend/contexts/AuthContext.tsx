'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { User as FirebaseUser, onAuthStateChanged, signOut } from 'firebase/auth';
import { auth } from '@/lib/firebase';
import ApiClient, { api } from '@/lib/api';

interface User {
  id: number;
  firebase_uid: string;
  phone: string;
  role: string;
  created_at: string;
  updated_at: string;
}

interface AuthContextType {
  user: User | null;
  firebaseUser: FirebaseUser | null;
  loading: boolean;
  error: string | null;
  refreshUser: () => Promise<void>;
  signOut: () => Promise<void>;
  initializeSession: (firebaseUser: FirebaseUser) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [firebaseUser, setFirebaseUser] = useState<FirebaseUser | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refreshUser = async () => {
    try {
      setError(null);
      
      // Try to get user from cookie session first
      const cookieUser = await api.getCurrentUserFromCookie();
      if (cookieUser) {
        setUser(cookieUser);
        return;
      }
      
      // Fallback to Firebase token-based authentication
      if (firebaseUser) {
        const backendUser = await api.getCurrentUser() as User;
        setUser(backendUser);
      }
    } catch (err) {
      console.error('Error refreshing user:', err);
      setError(err instanceof Error ? err.message : 'Failed to refresh user');
      setUser(null);
    }
  };

  const initializeSession = async (firebaseUser: FirebaseUser) => {
    try {
      setError(null);
      
      // Get Firebase tokens
      const idToken = await firebaseUser.getIdToken();
      const refreshToken = firebaseUser.refreshToken;
      
      if (refreshToken) {
        // Set cookies for session management
        await api.setAuthCookies(idToken, refreshToken);
        console.log('Session cookies set successfully');
      }
      
      // Get user from backend
      const backendUser = await api.getCurrentUser() as User;
      setUser(backendUser);
      
    } catch (err) {
      console.error('Error initializing session:', err);
      setError(err instanceof Error ? err.message : 'Failed to initialize session');
      setUser(null);
    }
  };

  const handleSignOut = async () => {
    try {
      // Clear cookies on the server
      await api.logout();
      
      // Sign out from Firebase
      await signOut(auth);
      
      setUser(null);
      setFirebaseUser(null);
      setError(null);
    } catch (err) {
      console.error('Error signing out:', err);
      setError(err instanceof Error ? err.message : 'Failed to sign out');
    }
  };

  const checkExistingSession = async () => {
    try {
      setError(null);
      
      // Check if we have a valid session
      const sessionResponse = await api.checkSession();
      
      if (sessionResponse.authenticated && sessionResponse.user) {
        setUser(sessionResponse.user);
        console.log('Existing session found');
      } else {
        console.log('No existing session found');
      }
    } catch (err) {
      console.error('Error checking existing session:', err);
      // Not setting error here as it's normal to not have a session
    }
  };

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      setFirebaseUser(firebaseUser);
      setLoading(true);
      setError(null);

      if (firebaseUser) {
        try {
          // Check if we already have a session
          await checkExistingSession();
          
          // If no session, initialize one
          if (!user) {
            await initializeSession(firebaseUser);
          }
        } catch (err) {
          console.error('Error during Firebase auth state change:', err);
          setError('Authentication error occurred');
        }
      } else {
        // No Firebase user, but check for existing session
        await checkExistingSession();
      }

      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  // Initial session check on component mount
  useEffect(() => {
    const initializeAuth = async () => {
      await checkExistingSession();
      setLoading(false);
    };

    initializeAuth();
  }, []);

  // Auto-refresh tokens periodically
  useEffect(() => {
    const refreshInterval = setInterval(async () => {
      if (user) {
        try {
          await api.refreshAuthToken();
          console.log('Token refreshed automatically');
        } catch (err) {
          console.error('Auto token refresh failed:', err);
          // If refresh fails, user might need to login again
          setUser(null);
        }
      }
    }, 24 * 60 * 60 * 1000); // Refresh every 24 hours (1 day)

    return () => clearInterval(refreshInterval);
  }, [user]);

  return (
    <AuthContext.Provider
      value={{
        user,
        firebaseUser,
        loading,
        error,
        refreshUser,
        signOut: handleSignOut,
        initializeSession,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export default AuthProvider;