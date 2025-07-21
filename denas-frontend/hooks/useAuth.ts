"use client";

import { useState, useEffect } from "react";
import { User, onAuthStateChanged, signOut } from "firebase/auth";

import { auth } from "@/lib/firebase";
import { getUserRole, setUserRole, clearUserRole } from "@/lib/auth";

interface AuthState {
  user: User | null;
  role: "admin" | "user" | null;
  loading: boolean;
  isAuthenticated: boolean;
  isAdmin: boolean;
}

interface AuthActions {
  logout: () => Promise<void>;
  setUserRole: (role: "admin" | "user") => void;
  clearUserRole: () => void;
}

export function useAuth(): AuthState & AuthActions {
  const [user, setUser] = useState<User | null>(null);
  const [role, setRole] = useState<"admin" | "user" | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setUser(user);

      if (user) {
        // Get role from localStorage
        const userRole = getUserRole();

        setRole(userRole);
      } else {
        setRole(null);
      }

      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  const logout = async () => {
    try {
      await signOut(auth);
      clearUserRole();
      setRole(null);
    } catch (error) {
      // console.error("Error signing out:", error);
    }
  };

  const handleSetUserRole = (newRole: "admin" | "user") => {
    setUserRole(newRole);
    setRole(newRole);
  };

  const handleClearUserRole = () => {
    clearUserRole();
    setRole(null);
  };

  return {
    user,
    role,
    loading,
    isAuthenticated: !!user,
    isAdmin: role === "admin",
    logout,
    setUserRole: handleSetUserRole,
    clearUserRole: handleClearUserRole,
  };
}

// Hook for checking if user can access admin routes
export function useAdminAccess() {
  const { isAdmin, loading, isAuthenticated } = useAuth();

  return {
    canAccess: isAdmin && isAuthenticated,
    loading,
    isAuthenticated,
    isAdmin,
  };
}

// Hook for protected routes
export function useProtectedRoute(requireAdmin: boolean = false) {
  const { user, role, loading, isAuthenticated, isAdmin, logout } = useAuth();

  const canAccess = requireAdmin ? isAdmin : isAuthenticated;

  return {
    user,
    role,
    loading,
    isAuthenticated,
    isAdmin,
    canAccess,
    logout,
  };
}
