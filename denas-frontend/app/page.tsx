"use client";

import React from "react";
import { Button } from "@heroui/button";
import { Card, CardBody, CardHeader } from "@heroui/card";
import { Spinner } from "@heroui/spinner";
import { useRouter } from "next/navigation";

import { useAuth } from "@/contexts/AuthContext";

export default function Home() {
  const { user, loading, error } = useAuth();
  const router = useRouter();

  // Auto-redirect users based on role
  React.useEffect(() => {
    if (user && user.role === "Admin") {
      console.log("Admin user detected, redirecting to admin panel");
      router.push("/admin");
    } else if (user && user.role !== "Admin") {
      console.log("Customer user detected, redirecting to client dashboard");
      router.push("/client");
    }
  }, [user, router]);

  // Show loading spinner while checking authentication
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Spinner size="lg" />
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Show error if there's an authentication error
  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="max-w-md">
          <CardHeader>
            <h3 className="text-lg font-semibold text-red-600">Error</h3>
          </CardHeader>
          <CardBody>
            <p className="text-gray-600 mb-4">{error}</p>
            <Button color="primary" onPress={() => router.push("/auth/login")}>
              Go to Login
            </Button>
          </CardBody>
        </Card>
      </div>
    );
  }

  // If user is not authenticated, show welcome page with login option
  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="container mx-auto px-4 py-16">
          <div className="text-center mb-12">
            <h1 className="text-5xl font-bold text-gray-900 mb-4">
              Welcome to Denas
            </h1>
            <p className="text-xl text-gray-600 mb-8">
              Your ultimate e-commerce destination
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
            <Card className="h-full">
              <CardHeader>
                <h3 className="text-lg font-semibold">🛍️ Shop Products</h3>
              </CardHeader>
              <CardBody>
                <p className="text-gray-600">
                  Browse our wide selection of products and find exactly what
                  you need.
                </p>
              </CardBody>
            </Card>

            <Card className="h-full">
              <CardHeader>
                <h3 className="text-lg font-semibold">📱 Easy Ordering</h3>
              </CardHeader>
              <CardBody>
                <p className="text-gray-600">
                  Simple and secure ordering process with multiple payment
                  options.
                </p>
              </CardBody>
            </Card>

            <Card className="h-full">
              <CardHeader>
                <h3 className="text-lg font-semibold">🚚 Fast Delivery</h3>
              </CardHeader>
              <CardBody>
                <p className="text-gray-600">
                  Quick and reliable delivery straight to your doorstep.
                </p>
              </CardBody>
            </Card>
          </div>

          <div className="text-center space-y-4">
            <div className="space-x-4">
              <Button
                color="primary"
                size="lg"
                onPress={() => router.push("/auth/login")}
              >
                Sign In
              </Button>
              <Button
                size="lg"
                variant="bordered"
                onPress={() => router.push("/auth/register")}
              >
                Create Account
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // If user is authenticated, they will be redirected by useEffect
  // This should not render for authenticated users
  return null;
}
