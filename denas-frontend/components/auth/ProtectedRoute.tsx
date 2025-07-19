'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { useProtectedRoute } from '@/hooks/useAuth';

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
  const { loading, canAccess, user } = useProtectedRoute(requireAdmin);
  const router = useRouter();

  React.useEffect(() => {
    if (!loading && !canAccess) {
      if (!user) {
        router.push('/auth/login');
      } else if (requireAdmin) {
        router.push('/');
      }
    }
  }, [loading, canAccess, user, router, requireAdmin]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
          <p className="mt-4 text-lg">Loading...</p>
        </div>
      </div>
    );
  }

  if (!canAccess) {
    return fallback || null;
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