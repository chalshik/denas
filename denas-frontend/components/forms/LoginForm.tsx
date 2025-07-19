'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { signInWithEmailAndPassword } from 'firebase/auth';
import { auth } from '@/lib/firebase';
import { Button } from '@heroui/button';
import { Input } from '@heroui/input';
import { Form } from '@heroui/form';
import { useForm } from '@/hooks/useForm';
import { useAuth } from '@/contexts/AuthContext';
import { api } from '@/lib/api';

interface LoginFormProps {
  onSwitchToRegister?: () => void;
}

export default function LoginForm({ onSwitchToRegister }: LoginFormProps) {
  const { form, setForm } = useForm({
    phoneNumber: '',
    password: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();
  const { initializeSession } = useAuth();

  // Convert phone number to email format for Firebase
  const phoneToEmail = (phone: string): string => {
    const cleanPhone = phone.replace(/\D/g, '');
    return `${cleanPhone}@phone.auth`;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!form.phoneNumber.trim() || !form.password.trim()) {
      setError('Please fill in all fields');
      return;
    }

    setIsLoading(true);
    setError('');
    
    try {
      const email = phoneToEmail(form.phoneNumber);
      
      // Sign in with Firebase
      const userCredential = await signInWithEmailAndPassword(auth, email, form.password);
      
      // Initialize session with backend (cookies + user data)
      await initializeSession(userCredential.user);
      
      // Get the user data to check role and redirect appropriately
      const userData = await api.getCurrentUser();
      
      console.log('User signed in successfully, role:', userData.role);
      
      // Redirect based on user role
      if (userData.role === 'Admin') {
        console.log('Redirecting admin to admin panel');
        router.push('/admin');
      } else {
        console.log('Redirecting user to dashboard');
        router.push('/');
      }
      
    } catch (error: any) {
      console.error('Login error:', error);
      
      if (error.code === 'auth/user-not-found') {
        setError('User not found. Please register first.');
      } else if (error.code === 'auth/wrong-password') {
        setError('Invalid password.');
      } else if (error.code === 'auth/invalid-email') {
        setError('Invalid phone number format.');
      } else {
        setError(error.message || 'Login failed');
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
          label="Phone Number"
          labelPlacement="outside"
          placeholder="Enter your phone number"
          value={form.phoneNumber}
          onValueChange={val => setForm(f => ({ ...f, phoneNumber: val }))}
          isRequired
          variant="bordered"
          classNames={{
            label: "text-gray-700 font-medium mb-2",
            input: "text-gray-900",
            inputWrapper: "border-gray-300"
          }}
        />
        
        <Input
          label="Password"
          labelPlacement="outside"
          placeholder="Enter your password"
          type="password"
          value={form.password}
          onValueChange={val => setForm(f => ({ ...f, password: val }))}
          isRequired
          variant="bordered"
          classNames={{
            label: "text-gray-700 font-medium mb-2",
            input: "text-gray-900",
            inputWrapper: "border-gray-300"
          }}
        />
        
        <Button
          type="submit"
          color="primary"
          className="w-full"
          isLoading={isLoading}
          size="lg"
        >
          Sign In
        </Button>
        
        {onSwitchToRegister && (
          <Button
            type="button"
            variant="light"
            className="w-full"
            onPress={onSwitchToRegister}
          >
            Don't have an account? Register
          </Button>
        )}
      </Form>
    </div>
  );
} 