"use client";

import React from "react";
import { Spinner } from "@heroui/spinner";
import { Card, CardBody } from "@heroui/card";
import { useRouter } from "next/navigation";

import { useAuth } from "@/contexts/AuthContext";

export default function ClientDashboard() {
  const { user, loading } = useAuth();
  const router = useRouter();

  // Redirect if not authenticated or if admin
  React.useEffect(() => {
    if (!loading && !user) {
      router.push("/auth/login");
    } else if (user && user.role === "Admin") {
      router.push("/admin");
    }
  }, [user, loading, router]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-center">
          <Spinner size="lg" />
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user || user.role === "Admin") {
    return null; // Will redirect via useEffect
  }

  const quickActions = [
    {
      title: "Browse Catalog",
      description: "Explore our product collection",
      icon: "🛍️",
      path: "/client/catalog",
      color: "primary",
    },
    {
      title: "View Favorites",
      description: "See your saved items",
      icon: "❤️",
      path: "/client/favorites",
      color: "secondary",
    },
    {
      title: "Shopping Cart",
      description: "Review your cart",
      icon: "🛒",
      path: "/client/cart",
      color: "success",
    },
  ];

  return (
    <div>
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          Welcome to Denas Shop
        </h2>
        <p className="text-gray-600">
          Hello {user.phone}! What would you like to do today?
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {quickActions.map((action) => (
          <Card
            key={action.path}
            isPressable
            className="cursor-pointer hover:shadow-lg transition-shadow group"
            onPress={() => router.push(action.path)}
          >
            <CardBody className="text-center p-6">
              <div className="text-4xl mb-3">{action.icon}</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {action.title}
              </h3>
              <p className="text-gray-600 mb-4">{action.description}</p>
              <div
                className={`w-full py-2 px-3 rounded-md text-sm font-medium transition-colors ${
                  action.color === "primary"
                    ? "bg-blue-100 text-blue-700 group-hover:bg-blue-200"
                    : action.color === "success"
                      ? "bg-green-100 text-green-700 group-hover:bg-green-200"
                      : "bg-purple-100 text-purple-700 group-hover:bg-purple-200"
                }`}
              >
                Go to {action.title}
              </div>
            </CardBody>
          </Card>
        ))}
      </div>

      {/* Quick Stats or Info Section */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="text-xl font-semibold text-gray-900 mb-4 text-center">
          Your Shopping Summary
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
          <div className="p-4 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">0</div>
            <div className="text-sm text-gray-600">Items in Cart</div>
          </div>
          <div className="p-4 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-red-500">0</div>
            <div className="text-sm text-gray-600">Favorite Items</div>
          </div>
          <div className="p-4 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-green-600">0</div>
            <div className="text-sm text-gray-600">Total Orders</div>
          </div>
        </div>
      </div>
    </div>
  );
}
