'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@heroui/button';
import { Link } from '@heroui/link';
import { useAuth } from '@/contexts/AuthContext';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { 
  ShoppingBagIcon, 
  ChatBubbleLeftRightIcon, 
  ChartBarIcon, 
  Cog6ToothIcon,
  ArrowRightOnRectangleIcon
} from '@heroicons/react/24/outline';

interface AdminLayoutProps {
  children: React.ReactNode;
}

export default function AdminLayout({ children }: AdminLayoutProps) {
  return (
    <ProtectedRoute requireAdmin>
      <AdminSidebarLayout>{children}</AdminSidebarLayout>
    </ProtectedRoute>
  );
}

function AdminSidebarLayout({ children }: { children: React.ReactNode }) {
  const { user, signOut } = useAuth();
  const router = useRouter();
  const menuItems = [
    {
      name: 'Dashboard',
      href: '/admin',
      icon: ChartBarIcon,
    },
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

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div className="w-64 bg-white shadow-lg flex flex-col">
        <div className="p-6">
          <h1 className="text-2xl font-bold text-gray-800">Admin Panel</h1>
          <p className="text-sm text-gray-600 mt-1">Welcome, {user?.phone}</p>
          <div className="text-xs text-gray-500 mt-1">Role: {user?.role}</div>
        </div>
        <nav className="mt-6 flex-1">
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
        <div className="p-4 mt-auto">
          <Button
            color="danger"
            variant="bordered"
            size="sm"
            className="w-full"
            startContent={<ArrowRightOnRectangleIcon className="w-4 h-4" />}
            onPress={async () => {
              await signOut();
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