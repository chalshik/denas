"use client";

import React from "react";
import { useRouter } from "next/navigation";
import { Card, CardBody, CardHeader } from "@heroui/card";
import { Button } from "@heroui/button";

import { useAuth } from "@/contexts/AuthContext";

export default function AdminDashboard() {
  const { user } = useAuth();
  const router = useRouter();

  const dashboardCards = [
    {
      title: "Products Management",
      description: "Add, edit, and manage your product catalog",
      icon: "🛍️",
      href: "/admin/products",
      color: "bg-blue-50 border-blue-200",
    },
    {
      title: "Customer Chats",
      description: "View and respond to customer inquiries",
      icon: "💬",
      href: "/admin/chats",
      color: "bg-green-50 border-green-200",
    },
    {
      title: "Analytics",
      description: "View sales reports and business insights",
      icon: "📊",
      href: "/admin/analytics",
      color: "bg-purple-50 border-purple-200",
    },
    {
      title: "Settings",
      description: "Configure system settings and preferences",
      icon: "⚙️",
      href: "/admin/settings",
      color: "bg-orange-50 border-orange-200",
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-gray-200 pb-6">
        <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
        <p className="text-gray-600 mt-2">
          Welcome back, {user?.phone}! Manage your e-commerce platform from
          here.
        </p>
        <div className="mt-2">
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
            {user?.role} Access
          </span>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="bg-gradient-to-r from-blue-500 to-blue-600 text-white">
          <CardBody className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-100">Total Products</p>
                <p className="text-2xl font-bold">--</p>
              </div>
              <div className="text-3xl">📦</div>
            </div>
          </CardBody>
        </Card>

        <Card className="bg-gradient-to-r from-green-500 to-green-600 text-white">
          <CardBody className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-100">Active Orders</p>
                <p className="text-2xl font-bold">--</p>
              </div>
              <div className="text-3xl">🛒</div>
            </div>
          </CardBody>
        </Card>

        <Card className="bg-gradient-to-r from-purple-500 to-purple-600 text-white">
          <CardBody className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-100">Total Users</p>
                <p className="text-2xl font-bold">--</p>
              </div>
              <div className="text-3xl">👥</div>
            </div>
          </CardBody>
        </Card>

        <Card className="bg-gradient-to-r from-orange-500 to-orange-600 text-white">
          <CardBody className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-orange-100">Revenue</p>
                <p className="text-2xl font-bold">$--</p>
              </div>
              <div className="text-3xl">💰</div>
            </div>
          </CardBody>
        </Card>
      </div>

      {/* Management Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {dashboardCards.map((card) => (
          <Card
            key={card.title}
            className={`hover:shadow-lg transition-shadow ${card.color}`}
          >
            <CardHeader className="flex gap-3">
              <div className="text-3xl">{card.icon}</div>
              <div className="flex flex-col">
                <h3 className="text-lg font-semibold text-gray-900">
                  {card.title}
                </h3>
              </div>
            </CardHeader>
            <CardBody className="pt-0">
              <p className="text-gray-600 mb-4">{card.description}</p>
              <Button
                color="primary"
                size="sm"
                variant="flat"
                onPress={() => router.push(card.href)}
              >
                Open {card.title}
              </Button>
            </CardBody>
          </Card>
        ))}
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold">Recent Activity</h3>
        </CardHeader>
        <CardBody>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="text-xl">📦</div>
                <div>
                  <p className="font-medium">System Ready</p>
                  <p className="text-sm text-gray-600">
                    Admin panel is configured and ready to use
                  </p>
                </div>
              </div>
              <span className="text-xs text-gray-500">Now</span>
            </div>
          </div>
        </CardBody>
      </Card>
    </div>
  );
}
