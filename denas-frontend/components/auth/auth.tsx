'use client';

import React, { useState } from 'react';
import { auth } from '@/lib/firebase';
import { createUserWithEmailAndPassword, signInWithEmailAndPassword } from 'firebase/auth';
import ApiClient from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { Card, CardBody, CardHeader, Input, Button, Spinner, Link } from '@heroui/react';

interface PhoneAuthProps {
  onSuccess?: () => void;
  onError?: (error: string) => void;
}

export const PhoneAuth: React.FC<PhoneAuthProps> = ({ onSuccess, onError }) => {
  const [phoneNumber, setPhoneNumber] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [isSignUp, setIsSignUp] = useState(false);
  const { refreshUser, initializeSession } = useAuth();

  const validateForm = () => {
    if (!phoneNumber.trim()) {
      onError?.('Please enter a phone number');
      return false;
    }
    if (!password.trim()) {
      onError?.('Please enter a password');
      return false;
    }
    if (password.length < 6) {
      onError?.('Password must be at least 6 characters');
      return false;
    }
    return true;
  };

  const phoneToEmail = (phone: string): string => {
    const cleanPhone = phone.replace(/\D/g, '');
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
        const userCredential = await createUserWithEmailAndPassword(auth, email, password);
        
        // Register user in backend
        await ApiClient.registerUser(phoneNumber);
        
        // Initialize session with cookies
        await initializeSession(userCredential.user);
        
        console.log('User registered and session initialized successfully');
        onSuccess?.();
      } else {
        // Sign in existing user
        const userCredential = await signInWithEmailAndPassword(auth, email, password);
        
        // Initialize session with cookies
        await initializeSession(userCredential.user);
        
        console.log('User signed in and session initialized successfully');
        onSuccess?.();
      }
    } catch (error: any) {
      console.error('Authentication error:', error);
      
      if (error.code === 'auth/user-not-found') {
        onError?.('User not found. Please sign up first.');
      } else if (error.code === 'auth/wrong-password') {
        onError?.('Invalid password.');
      } else if (error.code === 'auth/email-already-in-use') {
        onError?.('Phone number is already registered. Please sign in instead.');
      } else if (error.code === 'auth/weak-password') {
        onError?.('Password is too weak.');
      } else if (error.message?.includes('Failed to set authentication cookies')) {
        onError?.('Authentication successful but session setup failed. Please try again.');
      } else {
        onError?.(error.message || 'Authentication failed');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="max-w-md mx-auto shadow-lg">
      <CardHeader className="pb-0 pt-6 px-6">
        <h2 className="text-xl font-bold text-center w-full text-gray-800">
          {isSignUp ? 'Sign Up' : 'Sign In'}
        </h2>
        <p className="text-sm text-gray-600 text-center w-full mt-2">
          {isSignUp 
            ? 'Create a new account to get started' 
            : 'Welcome back! Please sign in to your account'
          }
        </p>
      </CardHeader>
      
      <CardBody className="px-6 pb-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          <Input
            type="tel"
            label="Phone Number"
            placeholder="Enter your phone number"
            value={phoneNumber}
            onValueChange={setPhoneNumber}
            isRequired
            variant="bordered"
            color="primary"
            classNames={{
              label: "text-gray-700 font-medium",
              input: "text-gray-900",
              inputWrapper: "border-gray-300 hover:border-blue-500 focus-within:border-blue-500"
            }}
          />
          
          <Input
            type="password"
            label="Password"
            placeholder="Enter your password"
            value={password}
            onValueChange={setPassword}
            isRequired
            minLength={6}
            variant="bordered"
            color="primary"
            classNames={{
              label: "text-gray-700 font-medium",
              input: "text-gray-900",
              inputWrapper: "border-gray-300 hover:border-blue-500 focus-within:border-blue-500"
            }}
          />
          
          <Button
            type="submit"
            color="primary"
            isLoading={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3"
            spinner={<Spinner color="white" size="sm" />}
          >
            {isSignUp ? 'Create Account' : 'Sign In'}
          </Button>
        </form>
        
        <div className="mt-6 text-center">
          <Link
            href="#"
            onPress={() => setIsSignUp(!isSignUp)}
            className="text-blue-600 hover:text-blue-800 font-medium"
          >
            {isSignUp ? 'Already have an account? Sign In' : 'Don\'t have an account? Sign Up'}
          </Link>
        </div>
        
        <div className="mt-4 text-center">
          <p className="text-xs text-gray-500">
            Your session will be automatically maintained across browser refreshes
          </p>
        </div>
      </CardBody>
    </Card>
  );
};

export default PhoneAuth; 