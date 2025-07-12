'use client';

import React, { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import PhoneAuth from '@/components/auth/auth';
import UserProfile from '@/components/auth/user-profile';
import { Spinner, Card, CardBody } from '@heroui/react';

export default function Home() {
  const { user, loading, error } = useAuth();
  const [authError, setAuthError] = useState<string | null>(null);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Spinner color="primary" size="lg" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Denas App</h1>
          <p className="text-gray-600 mt-2 font-medium">
            {user ? 'Welcome back!' : 'Sign in to continue'}
          </p>
        </div>

        {error && (
          <Card className="mb-4 border-red-200 bg-red-50">
            <CardBody>
              <div className="text-center text-red-700 font-medium">
                {error}
              </div>
            </CardBody>
          </Card>
        )}

        {authError && (
          <Card className="mb-4 border-red-200 bg-red-50">
            <CardBody>
              <div className="text-center text-red-700 font-medium">
                {authError}
              </div>
            </CardBody>
          </Card>
        )}

        {user ? (
          <UserProfile />
        ) : (
          <PhoneAuth
            onSuccess={() => {
              setAuthError(null);
              console.log('Authentication successful!');
            }}
            onError={(error) => {
              setAuthError(error);
            }}
          />
        )}
      </div>
    </div>
  );
}
