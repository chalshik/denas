'use client';

import React, { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRole } from '@/hooks/useRole';
import PhoneAuth from '@/components/auth/auth';
import UserProfile from '@/components/auth/user-profile';
import AdminLayout from '@/components/admin/layout/AdminLayout';
import ProductsManagement from '@/components/admin/products/ProductsManagement';
import ChatManagement from '@/components/admin/chat/ChatManagement';
import AnalyticsManagement from '@/components/admin/analytics/AnalyticsManagement';
import SettingsManagement from '@/components/admin/settings/SettingsManagement';
import { AdminOrManager } from '@/components/auth/RoleGuard';
import { Spinner, Card, CardBody, Button } from '@heroui/react';
import { Shield, User } from 'lucide-react';

export default function Home() {
  const { user, loading, error } = useAuth();
  const { hasAdminAccess } = useRole();
  const [authError, setAuthError] = useState<string | null>(null);
  const [showAdminPanel, setShowAdminPanel] = useState(false);
  const [activeTab, setActiveTab] = useState('products');

  // Automatically show admin panel for admins
  React.useEffect(() => {
    if (user && hasAdminAccess()) {
      setShowAdminPanel(true);
    }
  }, [user, hasAdminAccess]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Spinner color="primary" size="lg" />
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900">Denas App</h1>
            <p className="text-gray-600 mt-2 font-medium">
              Sign in to continue
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

          <PhoneAuth
            onSuccess={() => {
              setAuthError(null);
              console.log('Authentication successful!');
            }}
            onError={(error) => {
              setAuthError(error);
            }}
          />
        </div>
      </div>
    );
  }

  // Show admin panel if user has admin access and it's selected
  if (showAdminPanel && hasAdminAccess()) {
    return (
      <AdminOrManager>
        <AdminLayout
          title="Admin Dashboard"
          activeTab={activeTab}
          onTabChange={setActiveTab}
        >

          
          {activeTab === 'products' && <ProductsManagement />}
          {activeTab === 'chat' && <ChatManagement />}
          {activeTab === 'analytics' && <AnalyticsManagement />}
          {activeTab === 'settings' && <SettingsManagement />}
        </AdminLayout>
      </AdminOrManager>
    );
  }

  // Show user profile with admin access button
  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Denas App</h1>
          <p className="text-gray-600 mt-2 font-medium">
            Welcome back, {user.phone}!
          </p>
          <p className="text-sm text-gray-500 mt-1">
            Role: {user.role}
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

        {/* Admin Access Button */}
        {hasAdminAccess() && (
          <div className="mb-6 text-center">
            <Button
              color="primary"
              size="lg"
              startContent={<Shield className="h-5 w-5" />}
              onPress={() => setShowAdminPanel(true)}
              className="bg-gradient-to-r from-blue-600 to-purple-600 text-white"
            >
              Open Admin Dashboard
            </Button>
          </div>
        )}

        <UserProfile />
      </div>
    </div>
  );
}
