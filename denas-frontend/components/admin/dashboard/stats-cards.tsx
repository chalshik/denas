'use client';

import React from 'react';
import { Card, CardBody } from '@heroui/react';
import { Users, UserPlus, Calendar, TrendingUp } from 'lucide-react';
import { UserStats } from '@/types/auth';

interface StatsCardsProps {
  stats: UserStats;
}

const StatsCards: React.FC<StatsCardsProps> = ({ stats }) => {
  const statsData = [
    {
      title: 'Total Users',
      value: stats.total_users,
      icon: Users,
      color: 'text-blue-600',
      bg: 'bg-blue-50',
      iconBg: 'bg-blue-100',
    },
    {
      title: 'New Today',
      value: stats.users_today,
      icon: UserPlus,
      color: 'text-green-600',
      bg: 'bg-green-50',
      iconBg: 'bg-green-100',
    },
    {
      title: 'This Week',
      value: stats.users_this_week,
      icon: Calendar,
      color: 'text-purple-600',
      bg: 'bg-purple-50',
      iconBg: 'bg-purple-100',
    },
    {
      title: 'This Month',
      value: stats.users_this_month,
      icon: TrendingUp,
      color: 'text-orange-600',
      bg: 'bg-orange-50',
      iconBg: 'bg-orange-100',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {statsData.map((stat, index) => {
        const Icon = stat.icon;
        return (
          <Card key={index} className={`${stat.bg} border-0`}>
            <CardBody className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1">
                    {stat.title}
                  </p>
                  <p className={`text-3xl font-bold ${stat.color}`}>
                    {stat.value}
                  </p>
                </div>
                <div className={`p-3 rounded-lg ${stat.iconBg}`}>
                  <Icon className={`h-6 w-6 ${stat.color}`} />
                </div>
              </div>
            </CardBody>
          </Card>
        );
      })}
    </div>
  );
};

export default StatsCards; 