'use client';

import React, { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import PhoneAuth from '@/components/auth/PhoneAuth';
import UserProfile from '@/components/auth/UserProfile';

export default function Home() {
  const { user, loading, error } = useAuth();
  const [authError, setAuthError] = useState<string | null>(null);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Denas App</h1>
          <p className="text-gray-600 mt-2">
            {user ? 'Welcome back!' : 'Sign in to continue'}
          </p>
        </div>

        {error && (
          <div className="mb-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {authError && (
          <div className="mb-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {authError}
          </div>
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
