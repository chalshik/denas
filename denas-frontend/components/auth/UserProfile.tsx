'use client';

import React from 'react';
import { useAuth } from '@/contexts/AuthContext';

export const UserProfile: React.FC = () => {
  const { user, loading, error, signOut } = useAuth();

  if (loading) {
    return (
      <div className="flex justify-center items-center p-4">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        Error: {error}
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <div className="flex justify-between items-start mb-4">
        <h2 className="text-xl font-bold text-gray-900">User Profile</h2>
        <button
          onClick={signOut}
          className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 transition-colors"
        >
          Sign Out
        </button>
      </div>

      <div className="space-y-3">
        <div>
          <span className="font-semibold text-gray-700">ID:</span>
          <span className="ml-2 text-gray-900">{user.id}</span>
        </div>

        <div>
          <span className="font-semibold text-gray-700">Phone:</span>
          <span className="ml-2 text-gray-900">{user.phone}</span>
        </div>

        <div>
          <span className="font-semibold text-gray-700">Role:</span>
          <span className={`ml-2 px-2 py-1 rounded text-sm ${
            user.role === 'ADMIN' ? 'bg-red-100 text-red-800' :
            user.role === 'MANAGER' ? 'bg-yellow-100 text-yellow-800' :
            'bg-green-100 text-green-800'
          }`}>
            {user.role}
          </span>
        </div>

        <div>
          <span className="font-semibold text-gray-700">Created:</span>
          <span className="ml-2 text-gray-900">
            {new Date(user.created_at).toLocaleDateString()}
          </span>
        </div>

        <div>
          <span className="font-semibold text-gray-700">Firebase UID:</span>
          <span className="ml-2 text-gray-900 font-mono text-sm">{user.uid}</span>
        </div>
      </div>
    </div>
  );
};

export default UserProfile; 