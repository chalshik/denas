import React from 'react';
import { Button } from '@heroui/button';
import { Link } from '@heroui/link';

export default function ShopPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">Shop</h1>
        <p className="text-lg text-gray-600 mb-8">
          Browse our amazing products
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Placeholder product cards */}
          {[1, 2, 3, 4, 5, 6].map((item) => (
            <div key={item} className="border rounded-lg p-6 shadow-sm">
              <div className="w-full h-48 bg-gray-200 rounded-md mb-4"></div>
              <h3 className="text-lg font-semibold mb-2">Product {item}</h3>
              <p className="text-gray-600 mb-4">This is a sample product description.</p>
              <div className="flex justify-between items-center">
                <span className="text-xl font-bold">$99.99</span>
                <Button color="primary" size="sm">
                  Add to Cart
                </Button>
              </div>
            </div>
          ))}
        </div>
        
        <div className="mt-8">
          <Link href="/">
            <Button variant="bordered">
              Back to Home
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
