'use client';

import React from 'react';
import { useRole } from '@/hooks/useRole';
import { Card, CardBody, Button, Divider } from '@heroui/react';
import { User, Settings, BarChart3, Users, Package, MessageCircle } from 'lucide-react';

interface AdminLayoutProps {
  children: React.ReactNode;
  title: string;
  activeTab?: string;
  onTabChange?: (tab: string) => void;
}

export const AdminLayout: React.FC<AdminLayoutProps> = ({
  children,
  title,
  activeTab = 'dashboard',
  onTabChange
}) => {
  const { user, canAccess } = useRole();

  const tabs = [
    {
      id: 'products',
      label: 'Products',
      icon: Package,
      permission: 'canViewAdmin' as const,
    },
    {
      id: 'chat',
      label: 'Chat',
      icon: MessageCircle,
      permission: 'canViewAdmin' as const,
    },
    {
      id: 'analytics',
      label: 'Analytics',
      icon: BarChart3,
      permission: 'canViewAdmin' as const,
    },
    {
      id: 'settings',
      label: 'Settings',
      icon: Settings,
      permission: 'canViewAdmin' as const,
    },
  ];

  const availableTabs = tabs.filter(tab => canAccess(tab.permission));

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex justify-between items-center">
            <div className="flex space-x-8">
              {availableTabs.map((tab) => {
                const Icon = tab.icon;
                const isActive = activeTab === tab.id;
                return (
                  <button
                    key={tab.id}
                    onClick={() => onTabChange?.(tab.id)}
                    className={`flex items-center space-x-2 py-4 px-4 border-b-2 transition-colors ${
                      isActive 
                        ? 'border-blue-600 text-blue-600' 
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <Icon className="h-4 w-4" />
                    <span className="font-medium">{tab.label}</span>
                  </button>
                );
              })}
            </div>
            <div className="flex items-center space-x-2 py-4">
              <User className="h-5 w-5 text-gray-400" />
              <span className="text-sm text-gray-700">
                {user?.phone} ({user?.role})
              </span>
            </div>
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </div>
    </div>
  );
};

export default AdminLayout; 