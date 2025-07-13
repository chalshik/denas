'use client';

import React from 'react';
import { useAuth } from '@/app/hooks/useAuth';
import { Button } from '@heroui/button';
import { Card, CardBody, CardHeader } from '@heroui/card';
import { Input } from '@heroui/input';

export default function ProfilePage() {
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
          <p className="text-gray-600 mb-4">Please log in to view your profile.</p>
          <Button color="primary" href="/auth/login">
            Go to Login
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Profile</h1>
        
        <Card className="bg-white">
          <CardHeader className="pb-0 pt-6 px-6">
            <h2 className="text-xl font-semibold">User Information</h2>
          </CardHeader>
          <CardBody className="p-6 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email
              </label>
              <Input
                value={user?.email || ''}
                isReadOnly
                placeholder="Email"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                User ID
              </label>
              <Input
                value={user?.uid || ''}
                isReadOnly
                placeholder="User ID"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Account Created
              </label>
              <Input
                value={user?.metadata?.creationTime ? new Date(user.metadata.creationTime).toLocaleDateString() : ''}
                isReadOnly
                placeholder="Creation Date"
              />
            </div>
          </CardBody>
        </Card>
      </div>
    </div>
  );
}
