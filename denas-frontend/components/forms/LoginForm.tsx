'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { signInWithEmailAndPassword } from 'firebase/auth';
import { auth } from '@/lib/firebase';
import { Button } from '@heroui/button';
import { Input } from '@heroui/input';
import { Form } from '@heroui/form';
import { useForm } from '@/app/hooks/useForm';

interface LoginFormProps {
  onSwitchToRegister?: () => void;
}

export default function LoginForm({ onSwitchToRegister }: LoginFormProps) {
  const { form, setForm, handleInput } = useForm({
    phoneNumber: '',
    password: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();

  const handlePasswordLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    try {
      const email = `${form.phoneNumber}@phone.com`;
      const userCredential = await signInWithEmailAndPassword(auth, email, form.password);
      const idToken = await userCredential.user.getIdToken();
      const backendUser = await import('@/lib/auth').then(m => m.fetchUserProfile(idToken));
      localStorage.setItem('userRole', backendUser.role?.toLowerCase?.() || 'user');
      if (backendUser.role === 'Admin') {
        router.push('/admin/products');
      } else {
        router.push('/');
      }
    } catch (error: any) {
      setError(error.message || 'Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  const onSubmit = (e: React.FormEvent) => {
    handlePasswordLogin(e);
  };

  return (
    <div className="w-full max-w-md mx-auto flex flex-col items-center justify-center min-h-[60vh]">
      <Form
        className="w-full space-y-6"
        onSubmit={onSubmit}
      >
        <div className="space-y-6">
          <Input
            label="Phone Number"
            labelPlacement="outside"
            classNames={{ label: 'mb-2' }}
            placeholder="Enter your phone"
            value={form.phoneNumber}
            onValueChange={val => setForm(f => ({ ...f, phoneNumber: val }))}
            isInvalid={!!error}
            errorMessage={error || undefined}
          />
          <Input
            label="Password"
            labelPlacement="outside"
            classNames={{ label: 'mb-2' }}
            placeholder="Enter your password"
            type="password"
            value={form.password}
            onValueChange={val => setForm(f => ({ ...f, password: val }))}
          />
          <Button
            type="submit"
            color="primary"
            className="w-full"
            isLoading={isLoading}
          >
            Login
          </Button>
          <Button
            type="button"
            variant="bordered"
            className="w-full"
            onPress={onSwitchToRegister}
          >
            Don't have an account? Register
          </Button>
        </div>
      </Form>
    </div>
  );
} 