'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@heroui/button';
import { Link } from '@heroui/link';
import { useProtectedRoute } from '@/app/hooks/useAuth';
import { 
  ShoppingBagIcon, 
  ChatBubbleLeftRightIcon, 
  ChartBarIcon, 
  Cog6ToothIcon 
} from '@heroicons/react/24/outline';

interface AdminLayoutProps {
  children: React.ReactNode;
}

export default function AdminLayout({ children }: AdminLayoutProps) {
  const { user, loading, canAccess, logout } = useProtectedRoute(true);
  const router = useRouter();

  React.useEffect(() => {
    if (!loading && !canAccess) {
      if (!user) {
        router.push('/auth/login');
      } else {
        router.push('/');
      }
    }
  }, [loading, canAccess, user, router]);

  const menuItems = [
    {
      name: 'Products',
      href: '/admin/products',
      icon: ShoppingBagIcon,
    },
    {
      name: 'Chats',
      href: '/admin/chats',
      icon: ChatBubbleLeftRightIcon,
    },
    {
      name: 'Analytics',
      href: '/admin/analytics',
      icon: ChartBarIcon,
    },
    {
      name: 'Settings',
      href: '/admin/settings',
      icon: Cog6ToothIcon,
    },
  ];

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

  if (!user || !canAccess) {
    return null;
  }

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div className="w-64 bg-white shadow-lg">
        <div className="p-6">
          <h1 className="text-2xl font-bold text-gray-800">Admin Panel</h1>
          <p className="text-sm text-gray-600 mt-1">Welcome, {user.email}</p>
        </div>
        
        <nav className="mt-6">
          <div className="px-4 space-y-2">
            {menuItems.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className="flex items-center px-4 py-3 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <Icon className="w-5 h-5 mr-3" />
                  {item.name}
                </Link>
              );
            })}
          </div>
        </nav>

        <div className="absolute bottom-4 left-4 right-4">
          <Button
            color="danger"
            variant="bordered"
            className="w-full"
            onPress={async () => {
              await logout();
              router.push('/');
            }}
          >
            Sign Out
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        <div className="p-8">
          {children}
        </div>
      </div>
    </div>
  );
} 