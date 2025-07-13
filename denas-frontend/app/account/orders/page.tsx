'use client';

import React from 'react';
import { useAuth } from '@/app/hooks/useAuth';
import { Button } from '@heroui/button';
import { Card, CardBody, CardHeader } from '@heroui/card';

// Mock orders data
const mockOrders = [
  {
    id: 'ORD-001',
    date: '2024-01-15',
    status: 'Delivered',
    total: '$299.99',
    items: 3
  },
  {
    id: 'ORD-002',
    date: '2024-01-10',
    status: 'Processing',
    total: '$149.99',
    items: 2
  },
  {
    id: 'ORD-003',
    date: '2024-01-05',
    status: 'Shipped',
    total: '$89.99',
    items: 1
  }
];

export default function OrdersPage() {
  const { user, loading, isAuthenticated } = useAuth();

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

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Access Denied</h1>
          <p className="text-gray-600 mb-4">Please log in to view your orders.</p>
          <Button color="primary" href="/auth/login">
            Go to Login
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">My Orders</h1>
        
        <div className="space-y-4">
          {mockOrders.map((order) => (
            <Card key={order.id} className="bg-white">
              <CardBody className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold">{order.id}</h3>
                    <p className="text-sm text-gray-600">Ordered on {order.date}</p>
                    <p className="text-sm text-gray-600">{order.items} items</p>
                  </div>
                  
                  <div className="text-right">
                    <p className="text-lg font-bold">{order.total}</p>
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      order.status === 'Delivered' 
                        ? 'bg-green-100 text-green-800'
                        : order.status === 'Processing'
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-blue-100 text-blue-800'
                    }`}>
                      {order.status}
                    </span>
                  </div>
                </div>
                
                <div className="mt-4 flex gap-2">
                  <Button size="sm" variant="bordered">
                    View Details
                  </Button>
                  <Button size="sm" color="primary">
                    Track Order
                  </Button>
                </div>
              </CardBody>
            </Card>
          ))}
        </div>
        
        {mockOrders.length === 0 && (
          <div className="text-center py-12">
            <h3 className="text-lg font-semibold mb-2">No orders yet</h3>
            <p className="text-gray-600 mb-4">Start shopping to see your orders here.</p>
            <Button color="primary" href="/shop">
              Browse Products
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
