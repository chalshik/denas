'use client';

import React from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Spinner } from '@heroui/spinner';
import { useRouter } from 'next/navigation';
import Catalog from '@/components/Catalog';

export default function CatalogPage() {
  const { user, loading } = useAuth();
  const router = useRouter();

  // Redirect if not authenticated or if admin
  React.useEffect(() => {
    if (!loading && !user) {
      router.push('/auth/login');
    } else if (user && user.role === 'Admin') {
      router.push('/admin');
    }
  }, [user, loading, router]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-center">
          <Spinner size="lg" />
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user || user.role === 'Admin') {
    return null; // Will redirect via useEffect
  }

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Product Catalog</h2>
        <p className="text-gray-600">Browse our amazing products by category</p>
      </div>
      
      <Catalog />
    </div>
  );
} 