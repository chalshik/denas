'use client';

import React from 'react';
import { Card, CardBody, CardHeader } from '@heroui/card';

// Mock data for demonstration
const stats = [
  { title: 'Total Sales', value: '$45,231', change: '+20.1%', changeType: 'positive' },
  { title: 'Orders', value: '2,350', change: '+180.1%', changeType: 'positive' },
  { title: 'Customers', value: '1,234', change: '+19%', changeType: 'positive' },
  { title: 'Products', value: '573', change: '+201', changeType: 'positive' },
];

const recentOrders = [
  { id: 1, customer: 'John Doe', amount: '$299.00', status: 'Completed' },
  { id: 2, customer: 'Jane Smith', amount: '$199.00', status: 'Processing' },
  { id: 3, customer: 'Mike Johnson', amount: '$99.00', status: 'Completed' },
  { id: 4, customer: 'Sarah Wilson', amount: '$399.00', status: 'Pending' },
];

export default function AdminAnalyticsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
        <p className="text-gray-600 mt-2">Track your business performance</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <Card key={index} className="bg-white">
            <CardBody className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                  <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                </div>
                <div className={`text-sm ${
                  stat.changeType === 'positive' ? 'text-green-600' : 'text-red-600'
                }`}>
                  {stat.change}
                </div>
              </div>
            </CardBody>
          </Card>
        ))}
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sales Chart */}
        <Card className="bg-white">
          <CardHeader className="pb-0 pt-6 px-6">
            <h3 className="text-lg font-semibold">Sales Overview</h3>
          </CardHeader>
          <CardBody className="p-6">
            <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
              <p className="text-gray-500">Chart placeholder - Sales data</p>
            </div>
          </CardBody>
        </Card>

        {/* Orders Chart */}
        <Card className="bg-white">
          <CardHeader className="pb-0 pt-6 px-6">
            <h3 className="text-lg font-semibold">Orders Overview</h3>
          </CardHeader>
          <CardBody className="p-6">
            <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
              <p className="text-gray-500">Chart placeholder - Orders data</p>
            </div>
          </CardBody>
        </Card>
      </div>

      {/* Recent Orders */}
      <Card className="bg-white">
        <CardHeader className="pb-0 pt-6 px-6">
          <h3 className="text-lg font-semibold">Recent Orders</h3>
        </CardHeader>
        <CardBody className="p-6">
          <div className="space-y-4">
            {recentOrders.map((order) => (
              <div key={order.id} className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <p className="font-medium text-gray-900">{order.customer}</p>
                  <p className="text-sm text-gray-600">Order #{order.id}</p>
                </div>
                <div className="text-right">
                  <p className="font-medium text-gray-900">{order.amount}</p>
                  <span className={`px-2 py-1 rounded-full text-xs ${
                    order.status === 'Completed' 
                      ? 'bg-green-100 text-green-800'
                      : order.status === 'Processing'
                      ? 'bg-yellow-100 text-yellow-800'
                      : 'bg-gray-100 text-gray-800'
                  }`}>
                    {order.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </CardBody>
      </Card>
    </div>
  );
}
