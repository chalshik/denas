'use client';

import React, { useState } from 'react';
import { auth } from '@/lib/firebase';
import { createUserWithEmailAndPassword, signInWithEmailAndPassword } from 'firebase/auth';
import { ApiClient } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';

interface PhoneAuthProps {
  onSuccess?: () => void;
  onError?: (error: string) => void;
}

export const PhoneAuth: React.FC<PhoneAuthProps> = ({ onSuccess, onError }) => {
  const [phoneNumber, setPhoneNumber] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [isSignUp, setIsSignUp] = useState(false);
  const { refreshUser } = useAuth();

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
        await createUserWithEmailAndPassword(auth, email, password);
        
        // Register user in backend
        await ApiClient.registerUser(phoneNumber);
        
        // Refresh user data
        await refreshUser();
        onSuccess?.();
      } else {
        // Sign in existing user
        await signInWithEmailAndPassword(auth, email, password);
        
        // Refresh user data
        await refreshUser();
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
      } else {
        onError?.(error.message || 'Authentication failed');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto bg-white p-6 rounded-lg shadow-md">
      <div className="mb-6">
        <h2 className="text-xl font-bold text-gray-900 text-center">
          {isSignUp ? 'Sign Up' : 'Sign In'}
        </h2>
      </div>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="phone" className="block text-sm font-medium text-gray-700">
            Phone Number
          </label>
          <input
            id="phone"
            type="tel"
            value={phoneNumber}
            onChange={(e) => setPhoneNumber(e.target.value)}
            placeholder="+1234567890"
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            required
          />
        </div>
        
        <div>
          <label htmlFor="password" className="block text-sm font-medium text-gray-700">
            Password
          </label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter your password"
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            required
            minLength={6}
          />
        </div>
        
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Loading...' : (isSignUp ? 'Sign Up' : 'Sign In')}
        </button>
      </form>
      
      <div className="mt-4 text-center">
        <button
          onClick={() => setIsSignUp(!isSignUp)}
          className="text-blue-600 hover:text-blue-800 underline"
        >
          {isSignUp ? 'Already have an account? Sign In' : 'Don\'t have an account? Sign Up'}
        </button>
      </div>
    </div>
  );
};

export default PhoneAuth; 