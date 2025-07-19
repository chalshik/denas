'use client';

import React from 'react';
import { Card, CardBody, CardHeader } from '@heroui/card';

export default function AdminAnalyticsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
        <p className="text-gray-600 mt-2">Track your business performance</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Здесь будут реальные метрики */}
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sales Chart */}
        <div className="bg-white rounded-lg shadow">
          <div className="pb-0 pt-6 px-6">
            <h3 className="text-lg font-semibold">Sales Overview</h3>
          </div>
          <div className="p-6">
            <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
              <p className="text-gray-500">Chart placeholder - Sales data</p>
            </div>
          </div>
        </div>

        {/* Orders Chart */}
        <div className="bg-white rounded-lg shadow">
          <div className="pb-0 pt-6 px-6">
            <h3 className="text-lg font-semibold">Orders Overview</h3>
          </div>
          <div className="p-6">
            <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
              <p className="text-gray-500">Chart placeholder - Orders data</p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Orders */}
      <div className="bg-white rounded-lg shadow">
        <div className="pb-0 pt-6 px-6">
          <h3 className="text-lg font-semibold">Recent Orders</h3>
        </div>
        <div className="p-6">
          {/* Здесь будет список заказов */}
        </div>
      </div>
    </div>
  );
}
