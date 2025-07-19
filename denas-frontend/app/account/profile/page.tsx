'use client';

import React from 'react';
import { useAuth } from '@/hooks/useAuth';
import { Button } from '@heroui/button';
import { Card, CardBody, CardHeader } from '@heroui/card';
import { Input } from '@heroui/input';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';

export default function ProfilePage() {
  return (
    <ProtectedRoute>
      <ProfileContent />
    </ProtectedRoute>
  );
}

function ProfileContent() {
  const { user } = useAuth();
  return (
    <div className="max-w-xl mx-auto">
      <Card>
        <CardHeader>
          <h1 className="text-2xl font-bold">Profile</h1>
        </CardHeader>
        <CardBody>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
              <Input value={user?.email || ''} readOnly />
            </div>
            {/* Добавьте другие поля профиля по необходимости */}
          </div>
        </CardBody>
      </Card>
    </div>
  );
}
