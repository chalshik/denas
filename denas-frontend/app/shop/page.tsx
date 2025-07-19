'use client';

import React from 'react';
import { Button } from '@heroui/button';
import { Link } from '@heroui/link';
import { Navbar } from '@/components/navbar';

export default function ShopPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <div className="container mx-auto px-4 py-8">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-4">Shop</h1>
          <p className="text-lg text-gray-600 mb-8">
            Browse our amazing products
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Placeholder product cards */}
          {[1, 2, 3, 4, 5, 6].map((item) => (
            <div key={item} className="bg-white border rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow">
              <div className="w-full h-48 bg-gray-200 rounded-md mb-4 flex items-center justify-center">
                <span className="text-gray-500">Product Image</span>
              </div>
              <h3 className="text-lg font-semibold mb-2">Product {item}</h3>
              <p className="text-gray-600 mb-4">This is a sample product description that describes the amazing features of this product.</p>
              <div className="flex justify-between items-center">
                <span className="text-xl font-bold text-green-600">$99.99</span>
                <Button color="primary" size="sm">
                  Add to Cart
                </Button>
              </div>
            </div>
          ))}
        </div>
        
        <div className="mt-12 text-center">
          <p className="text-gray-600 mb-4">
            Want to see real products? Sign in to access our full catalog!
          </p>
          <div className="space-x-4">
            <Link href="/auth/login">
              <Button color="primary">
                Sign In
              </Button>
            </Link>
            <Link href="/">
              <Button variant="bordered">
                Back to Home
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
