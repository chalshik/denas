"use client";

import React from "react";
import { useRouter } from "next/navigation";
import { Button } from "@heroui/button";

import RegisterForm from "@/components/forms/RegisterForm";

export default function RegisterPage() {
  const router = useRouter();

  const handleSwitchToLogin = () => {
    router.push("/auth/login");
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Create your account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Enter your phone number and any password (minimum 3 characters)
          </p>
        </div>

        <RegisterForm onSwitchToLogin={handleSwitchToLogin} />

        <div className="text-center">
          <Button size="sm" variant="light" onPress={() => router.push("/")}>
            Back to Home
          </Button>
        </div>
      </div>
    </div>
  );
}
