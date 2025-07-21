'use client';

import React from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Spinner } from '@heroui/spinner';
import { Button } from '@heroui/button';
import { useRouter } from 'next/navigation';

export default function FavoritesPage() {
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
    <div className="text-center">
      <h2 className="text-3xl font-bold text-gray-900 mb-4">Your Favorites</h2>
      <p className="text-gray-600 mb-8">Save products you love for later</p>
      
      <div className="bg-white rounded-lg shadow-sm p-8">
        <div className="text-6xl mb-4">❤️</div>
        <h3 className="text-xl font-semibold text-gray-900 mb-2">No Favorites Yet</h3>
        <p className="text-gray-600 mb-6">
          Start browsing products and add items to your favorites list!
        </p>
        <Button 
          color="primary" 
          onPress={() => router.push('/client/catalog')}
        >
          Browse Catalog
        </Button>
      </div>
    </div>
  );
} 