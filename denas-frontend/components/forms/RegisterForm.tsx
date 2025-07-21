"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { createUserWithEmailAndPassword } from "firebase/auth";
import { Button } from "@heroui/button";
import { Input } from "@heroui/input";
import { Form } from "@heroui/form";

import { auth } from "@/lib/firebase";
import { useForm } from "@/hooks/useForm";
import { useAuth } from "@/contexts/AuthContext";
import { api } from "@/lib/api";

interface RegisterFormProps {
  onSwitchToLogin?: () => void;
}

export default function RegisterForm({ onSwitchToLogin }: RegisterFormProps) {
  const { form, setForm } = useForm({
    phoneNumber: "",
    password: "",
    confirmPassword: "",
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const router = useRouter();
  const { initializeSession } = useAuth();

  // Convert phone number to email format for Firebase
  const phoneToEmail = (phone: string): string => {
    const cleanPhone = phone.replace(/\D/g, "");

    return `${cleanPhone}@phone.auth`;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!form.phoneNumber.trim() || !form.password.trim()) {
      setError("Please fill in all fields");

      return;
    }

    if (form.password !== form.confirmPassword) {
      setError("Passwords do not match");

      return;
    }

    // Simple password validation - just minimum length
    if (form.password.length < 3) {
      setError("Password must be at least 3 characters");

      return;
    }

    setIsLoading(true);
    setError("");

    try {
      const email = phoneToEmail(form.phoneNumber);

      // Create Firebase user
      const userCredential = await createUserWithEmailAndPassword(
        auth,
        email,
        form.password,
      );

      // Register user in backend database
      await api.registerUser(form.phoneNumber);

      // Initialize session with backend (cookies + user data)
      await initializeSession(userCredential.user);

      // Get the user data to check role and redirect appropriately
      const userData = await api.getCurrentUser();

      console.log("User registered successfully, role:", userData.role);

      // Redirect based on user role
      if (userData.role === "Admin") {
        console.log("Redirecting admin to admin panel");
        router.push("/admin");
      } else {
        console.log("Redirecting user to dashboard");
        router.push("/");
      }
    } catch (error: any) {
      console.error("Registration error:", error);

      if (error.code === "auth/email-already-in-use") {
        setError("Phone number is already registered. Please sign in instead.");
      } else if (error.code === "auth/weak-password") {
        setError("Password is too weak.");
      } else if (error.code === "auth/invalid-email") {
        setError("Invalid phone number format.");
      } else if (error.message?.includes("already exists")) {
        setError("Phone number is already registered. Please sign in instead.");
      } else {
        setError(error.message || "Registration failed");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md mx-auto">
      <Form className="w-full space-y-6" onSubmit={handleSubmit}>
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        <Input
          isRequired
          classNames={{
            label: "text-gray-700 font-medium mb-2",
            input: "text-gray-900",
            inputWrapper: "border-gray-300",
          }}
          label="Phone Number"
          labelPlacement="outside"
          placeholder="Enter your phone number"
          value={form.phoneNumber}
          variant="bordered"
          onValueChange={(val) => setForm((f) => ({ ...f, phoneNumber: val }))}
        />

        <Input
          isRequired
          classNames={{
            label: "text-gray-700 font-medium mb-2",
            input: "text-gray-900",
            inputWrapper: "border-gray-300",
          }}
          label="Password"
          labelPlacement="outside"
          placeholder="Enter any password (min 3 characters)"
          type="password"
          value={form.password}
          variant="bordered"
          onValueChange={(val) => setForm((f) => ({ ...f, password: val }))}
        />

        <Input
          isRequired
          classNames={{
            label: "text-gray-700 font-medium mb-2",
            input: "text-gray-900",
            inputWrapper: "border-gray-300",
          }}
          errorMessage={
            form.password !== form.confirmPassword &&
            form.confirmPassword.length > 0
              ? "Passwords do not match"
              : undefined
          }
          isInvalid={
            form.password !== form.confirmPassword &&
            form.confirmPassword.length > 0
          }
          label="Confirm Password"
          labelPlacement="outside"
          placeholder="Confirm your password"
          type="password"
          value={form.confirmPassword}
          variant="bordered"
          onValueChange={(val) =>
            setForm((f) => ({ ...f, confirmPassword: val }))
          }
        />

        <Button
          className="w-full"
          color="primary"
          isLoading={isLoading}
          size="lg"
          type="submit"
        >
          Create Account
        </Button>

        {onSwitchToLogin && (
          <Button
            className="w-full"
            type="button"
            variant="light"
            onPress={onSwitchToLogin}
          >
            Already have an account? Sign In
          </Button>
        )}
      </Form>
    </div>
  );
}
