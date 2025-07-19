'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { Spinner } from '@heroui/spinner';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requireAdmin?: boolean;
  fallback?: React.ReactNode;
}

export function ProtectedRoute({ 
  children, 
  requireAdmin = false, 
  fallback 
}: ProtectedRouteProps) {
  const { user, loading, error } = useAuth();
  const router = useRouter();

  React.useEffect(() => {
    if (!loading && !error) {
      if (!user) {
        // Not authenticated, redirect to login
        console.log('User not authenticated, redirecting to login');
        router.push('/auth/login');
      } else if (requireAdmin && user.role !== 'Admin') {
        // User is not admin but admin access required
        console.log('User is not admin, redirecting to home');
        router.push('/');
      }
    }
  }, [loading, error, user, router, requireAdmin]);

  // Show loading spinner while checking authentication
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Spinner size="lg" />
          <p className="mt-4 text-lg text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Show error if there's an authentication error
  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="bg-red-50 border border-red-200 text-red-700 px-6 py-4 rounded">
            <h3 className="font-semibold">Authentication Error</h3>
            <p className="mt-1">{error}</p>
          </div>
          <button 
            onClick={() => router.push('/auth/login')}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Go to Login
          </button>
        </div>
      </div>
    );
  }

  // Check if user is authenticated
  if (!user) {
    return fallback || null;
  }

  // Check admin requirement
  if (requireAdmin && user.role !== 'Admin') {
    return fallback || (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="bg-yellow-50 border border-yellow-200 text-yellow-700 px-6 py-4 rounded">
            <h3 className="font-semibold">Access Denied</h3>
            <p className="mt-1">You need admin privileges to access this page.</p>
          </div>
          <button 
            onClick={() => router.push('/')}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Go to Home
          </button>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}

// Convenience component for admin-only routes
export function AdminRoute({ children, fallback }: { 
  children: React.ReactNode; 
  fallback?: React.ReactNode; 
}) {
  return (
    <ProtectedRoute requireAdmin fallback={fallback}>
      {children}
    </ProtectedRoute>
  );
}

// Convenience component for authenticated routes
export function AuthRoute({ children, fallback }: { 
  children: React.ReactNode; 
  fallback?: React.ReactNode; 
}) {
  return (
    <ProtectedRoute fallback={fallback}>
      {children}
    </ProtectedRoute>
  );
} 