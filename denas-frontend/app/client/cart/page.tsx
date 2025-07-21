'use client';

import React from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Spinner } from '@heroui/spinner';
import { Button } from '@heroui/button';
import { Divider } from '@heroui/divider';
import { useRouter } from 'next/navigation';

export default function CartPage() {
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
      <h2 className="text-3xl font-bold text-gray-900 mb-4 text-center">Shopping Cart</h2>
      <p className="text-gray-600 mb-8 text-center">Review your items before checkout</p>
      
      <div className="bg-white rounded-lg shadow-sm p-8 max-w-2xl mx-auto">
        <div className="text-center">
          <div className="text-6xl mb-4">🛒</div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Your Cart is Empty</h3>
          <p className="text-gray-600 mb-6">
            Add some products to your cart to get started!
          </p>
          
          <Divider className="my-6" />
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button 
              color="primary" 
              onPress={() => router.push('/client/catalog')}
            >
              Continue Shopping
            </Button>
            <Button 
              variant="bordered" 
              onPress={() => router.push('/client/favorites')}
            >
              View Favorites
            </Button>
          </div>
          
          {/* Placeholder for future cart summary */}
          <div className="mt-8 p-4 bg-gray-50 rounded-lg">
            <h4 className="text-lg font-semibold text-gray-900 mb-2">Order Summary</h4>
            <div className="flex justify-between text-gray-600 mb-1">
              <span>Subtotal:</span>
              <span>$0.00</span>
            </div>
            <div className="flex justify-between text-gray-600 mb-1">
              <span>Shipping:</span>
              <span>$0.00</span>
            </div>
            <Divider className="my-2" />
            <div className="flex justify-between font-semibold text-gray-900">
              <span>Total:</span>
              <span>$0.00</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 