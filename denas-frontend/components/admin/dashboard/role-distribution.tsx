'use client';

import React from 'react';
import { Card, CardHeader, CardBody, Chip, Progress } from '@heroui/react';
import { Shield, User, Crown } from 'lucide-react';
import { UserStats, UserRole } from '@/types/auth';

interface RoleDistributionProps {
  stats: UserStats;
}

const RoleDistribution: React.FC<RoleDistributionProps> = ({ stats }) => {
  const total = stats.total_users;
  
  const roleData = [
    {
      role: UserRole.USER,
      count: stats.users_by_role[UserRole.USER],
      icon: User,
      color: 'primary',
      bgColor: 'bg-blue-50',
      textColor: 'text-blue-600',
    },
    {
      role: UserRole.MANAGER,
      count: stats.users_by_role[UserRole.MANAGER],
      icon: Shield,
      color: 'warning',
      bgColor: 'bg-orange-50',
      textColor: 'text-orange-600',
    },
    {
      role: UserRole.ADMIN,
      count: stats.users_by_role[UserRole.ADMIN],
      icon: Crown,
      color: 'danger',
      bgColor: 'bg-red-50',
      textColor: 'text-red-600',
    },
  ];

  const getPercentage = (count: number) => {
    return total > 0 ? Math.round((count / total) * 100) : 0;
  };

  return (
    <Card>
      <CardHeader>
        <h3 className="text-lg font-semibold">Role Distribution</h3>
      </CardHeader>
      <CardBody className="space-y-4">
        {roleData.map((role) => {
          const Icon = role.icon;
          const percentage = getPercentage(role.count);
          
          return (
            <div key={role.role} className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className={`p-2 rounded-lg ${role.bgColor}`}>
                    <Icon className={`h-4 w-4 ${role.textColor}`} />
                  </div>
                  <span className="font-medium">{role.role}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-medium">{role.count}</span>
                  <Chip
                    color={role.color as any}
                    size="sm"
                    variant="flat"
                  >
                    {percentage}%
                  </Chip>
                </div>
              </div>
              <Progress
                value={percentage}
                color={role.color as any}
                className="w-full"
                size="sm"
              />
            </div>
          );
        })}
        
        <div className="mt-6 pt-4 border-t border-gray-200">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Total Users</span>
            <span className="font-bold text-lg">{total}</span>
          </div>
        </div>
      </CardBody>
    </Card>
  );
};

export default RoleDistribution; 