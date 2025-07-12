'use client';

import React from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Card, CardBody, CardHeader, Button, Spinner, Chip } from '@heroui/react';

export const UserProfile: React.FC = () => {
  const { user, loading, error, signOut } = useAuth();

  if (loading) {
    return (
      <div className="flex justify-center items-center p-4">
        <Spinner color="primary" size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <Card className="max-w-md mx-auto border-red-200 bg-red-50">
        <CardBody>
          <div className="text-center text-red-700 font-medium">
            Error: {error}
          </div>
        </CardBody>
      </Card>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <Card className="max-w-md mx-auto shadow-lg">
      <CardHeader className="flex justify-between items-center pb-0 pt-6 px-6">
        <h2 className="text-xl font-bold text-gray-800">User Profile</h2>
        <Button
          color="danger"
          variant="solid"
          onPress={signOut}
          size="sm"
          className="bg-red-600 hover:bg-red-700 text-white font-medium"
        >
          Sign Out
        </Button>
      </CardHeader>

      <CardBody className="px-6 pb-6">
        <div className="space-y-4">
          <div className="flex flex-col gap-1">
            <span className="text-sm font-semibold text-gray-700">ID:</span>
            <span className="text-gray-900 font-medium">{user.id}</span>
          </div>

          <div className="flex flex-col gap-1">
            <span className="text-sm font-semibold text-gray-700">Phone:</span>
            <span className="text-gray-900 font-medium">{user.phone}</span>
          </div>

          <div className="flex flex-col gap-1">
            <span className="text-sm font-semibold text-gray-700">Role:</span>
            <Chip
              color={
                user.role === 'ADMIN' ? 'danger' :
                user.role === 'MANAGER' ? 'warning' :
                'success'
              }
              variant="solid"
              size="sm"
              className="font-medium"
            >
              {user.role}
            </Chip>
          </div>

          <div className="flex flex-col gap-1">
            <span className="text-sm font-semibold text-gray-700">Created:</span>
            <span className="text-gray-900 font-medium">
              {new Date(user.created_at).toLocaleDateString()}
            </span>
          </div>

          <div className="flex flex-col gap-1">
            <span className="text-sm font-semibold text-gray-700">Firebase UID:</span>
            <span className="text-gray-900 font-mono text-sm break-all">{user.uid}</span>
          </div>
        </div>
      </CardBody>
    </Card>
  );
};

export default UserProfile; 