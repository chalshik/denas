'use client';

import React, { useState, useEffect } from 'react';
import { useRole } from '@/hooks/useRole';
import { UserStats, UserListResponse } from '@/types/auth';
import { 
  Card, 
  CardHeader, 
  CardBody, 
  Button, 
  Spinner,
  Chip
} from '@heroui/react';
import { Users, UserPlus, Shield, TrendingUp } from 'lucide-react';
import { ApiClient } from '@/lib/api';

import StatsCards from './StatsCards';
import RecentUsers from './RecentUsers';
import RoleDistribution from './RoleDistribution';

export const AdminDashboard: React.FC = () => {
  const { canAccess } = useRole();
  const [stats, setStats] = useState<UserStats | null>(null);
  const [recentUsers, setRecentUsers] = useState<UserListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      const promises = [];
      
      if (canAccess('canViewStats')) {
        promises.push(fetchStats());
      }
      
      if (canAccess('canManageUsers')) {
        promises.push(fetchRecentUsers());
      }

      await Promise.all(promises);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/v1/auth/admin/stats', {
        headers: {
          'Authorization': `Bearer ${await ApiClient.getToken()}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (err) {
      console.error('Error fetching stats:', err);
    }
  };

  const fetchRecentUsers = async () => {
    try {
      const response = await fetch('/api/v1/auth/admin/users?limit=10&page=1', {
        headers: {
          'Authorization': `Bearer ${await ApiClient.getToken()}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setRecentUsers(data);
      }
    } catch (err) {
      console.error('Error fetching recent users:', err);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-96">
        <Spinner color="primary" size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <Card className="border-red-200 bg-red-50">
        <CardBody className="text-center">
          <p className="text-red-700 font-medium">{error}</p>
          <Button
            color="primary"
            className="mt-4"
            onPress={fetchDashboardData}
          >
            Try Again
          </Button>
        </CardBody>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      {stats && canAccess('canViewStats') && (
        <StatsCards stats={stats} />
      )}

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Role Distribution */}
        {stats && canAccess('canViewStats') && (
          <div className="lg:col-span-1">
            <RoleDistribution stats={stats} />
          </div>
        )}

        {/* Recent Users */}
        {recentUsers && canAccess('canManageUsers') && (
          <div className="lg:col-span-2">
            <RecentUsers 
              users={recentUsers.users} 
              onRefresh={fetchRecentUsers}
            />
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex justify-center space-x-4">
        <Button
          color="primary"
          startContent={<TrendingUp className="h-4 w-4" />}
          onPress={fetchDashboardData}
        >
          Refresh Data
        </Button>
        
        {canAccess('canManageUsers') && (
          <Button
            color="secondary"
            variant="bordered"
            startContent={<Users className="h-4 w-4" />}
          >
            View All Users
          </Button>
        )}
      </div>
    </div>
  );
};

export default AdminDashboard; 