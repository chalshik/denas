"use client";

import React, { useState } from "react";
import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
} from "firebase/auth";
import { Card, CardBody, CardHeader } from "@heroui/card";
import { Input } from "@heroui/input";
import { Button } from "@heroui/button";
import { Spinner } from "@heroui/spinner";
import { Link } from "@heroui/link";

import { useAuth } from "@/contexts/AuthContext";
import { api } from "@/lib/api";
import { auth } from "@/lib/firebase";

interface PhoneAuthProps {
  onSuccess?: () => void;
  onError?: (error: string) => void;
}

export const PhoneAuth: React.FC<PhoneAuthProps> = ({ onSuccess, onError }) => {
  const [phoneNumber, setPhoneNumber] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [isSignUp, setIsSignUp] = useState(false);
  const { initializeSession } = useAuth();

  const validateForm = () => {
    if (!phoneNumber.trim()) {
      onError?.("Please enter a phone number");

      return false;
    }
    if (!password.trim()) {
      onError?.("Please enter a password");

      return false;
    }
    // Simple validation - just minimum length
    if (password.length < 3) {
      onError?.("Password must be at least 3 characters");

      return false;
    }

    return true;
  };

  const phoneToEmail = (phone: string): string => {
    const cleanPhone = phone.replace(/\D/g, "");

    return `${cleanPhone}@phone.auth`;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) return;

    setLoading(true);
    try {
      const email = phoneToEmail(phoneNumber);

      if (isSignUp) {
        // Sign up new user
        const userCredential = await createUserWithEmailAndPassword(
          auth,
          email,
          password,
        );

        // Register user in backend
        await api.registerUser(phoneNumber);

        // Initialize session with cookies
        await initializeSession(userCredential.user);

        console.log("User registered and session initialized successfully");
        onSuccess?.();
      } else {
        // Sign in existing user
        const userCredential = await signInWithEmailAndPassword(
          auth,
          email,
          password,
        );

        // Initialize session with cookies
        await initializeSession(userCredential.user);

        console.log("User signed in and session initialized successfully");
        onSuccess?.();
      }
    } catch (error: any) {
      console.error("Authentication error:", error);

      if (error.code === "auth/user-not-found") {
        onError?.("User not found. Please sign up first.");
      } else if (error.code === "auth/wrong-password") {
        onError?.("Invalid password.");
      } else if (error.code === "auth/email-already-in-use") {
        onError?.(
          "Phone number is already registered. Please sign in instead.",
        );
      } else if (error.code === "auth/weak-password") {
        onError?.("Password is too weak.");
      } else if (
        error.message?.includes("Failed to set authentication cookies")
      ) {
        onError?.(
          "Authentication successful but session setup failed. Please try again.",
        );
      } else if (error.message?.includes("already exists")) {
        onError?.(
          "Phone number is already registered. Please sign in instead.",
        );
      } else {
        onError?.(error.message || "Authentication failed");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="max-w-md mx-auto shadow-lg">
      <CardHeader className="pb-0 pt-6 px-6">
        <h2 className="text-xl font-bold text-center w-full text-gray-800">
          {isSignUp ? "Sign Up" : "Sign In"}
        </h2>
        <p className="text-sm text-gray-600 text-center w-full mt-2">
          {isSignUp
            ? "Create a new account to get started"
            : "Welcome back! Please sign in to your account"}
        </p>
      </CardHeader>

      <CardBody className="px-6 pb-6">
        <form className="space-y-6" onSubmit={handleSubmit}>
          <Input
            isRequired
            classNames={{
              label: "text-gray-700 font-medium",
              input: "text-gray-900",
              inputWrapper:
                "border-gray-300 hover:border-blue-500 focus-within:border-blue-500",
            }}
            color="primary"
            label="Phone Number"
            placeholder="Enter your phone number"
            type="tel"
            value={phoneNumber}
            variant="bordered"
            onValueChange={setPhoneNumber}
          />

          <Input
            isRequired
            classNames={{
              label: "text-gray-700 font-medium",
              input: "text-gray-900",
              inputWrapper:
                "border-gray-300 hover:border-blue-500 focus-within:border-blue-500",
            }}
            color="primary"
            label="Password"
            placeholder={
              isSignUp
                ? "Enter any password (min 3 chars)"
                : "Enter your password"
            }
            type="password"
            value={password}
            variant="bordered"
            onValueChange={setPassword}
          />

          <Button
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3"
            color="primary"
            isLoading={loading}
            spinner={<Spinner color="white" size="sm" />}
            type="submit"
          >
            {isSignUp ? "Create Account" : "Sign In"}
          </Button>
        </form>

        <div className="mt-6 text-center">
          <Link
            className="text-blue-600 hover:text-blue-800 font-medium"
            href="#"
            onPress={() => setIsSignUp(!isSignUp)}
          >
            {isSignUp
              ? "Already have an account? Sign In"
              : "Don't have an account? Sign Up"}
          </Link>
        </div>

        <div className="mt-4 text-center">
          <p className="text-xs text-gray-500">
            Your session will be automatically maintained across browser
            refreshes
          </p>
        </div>
      </CardBody>
    </Card>
  );
};

export default PhoneAuth;
