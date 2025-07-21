'use client';

import React from 'react';
import { Button } from '@heroui/button';
import { useRouter } from 'next/navigation';

export default function ShopPage() {
  const router = useRouter();

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-4">Shop</h1>
          <p className="text-lg text-gray-600 mb-8">
            Welcome to our shop. Coming soon!
          </p>
          
          <Button 
            variant="bordered" 
            onPress={() => router.back()}
          >
            Go Back
          </Button>
        </div>
      </div>
    </div>
  );
} 