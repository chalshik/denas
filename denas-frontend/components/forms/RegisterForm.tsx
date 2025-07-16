'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { createUserWithEmailAndPassword } from 'firebase/auth';
import { auth } from '@/lib/firebase';
import { Button } from '@heroui/button';
import { Input } from '@heroui/input';
import { Form } from '@heroui/form';
import { useForm } from '@/hooks/useForm';

interface RegisterFormProps {
  onSwitchToLogin?: () => void;
}

export default function RegisterForm({ onSwitchToLogin }: RegisterFormProps) {
  const { form, setForm, handleInput } = useForm({
    phoneNumber: '',
    password: '',
    confirmPassword: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();

  const getPasswordError = (value: string) => {
    if (value.length < 6) {
      return "Password must be at least 6 characters";
    }
    if (!/(?=.*[A-Z])/.test(value)) {
      return "Password needs at least 1 uppercase letter";
    }
    if (!/(?=.*[0-9])/.test(value)) {
      return "Password needs at least 1 number";
    }
    return null;
  };

  const handlePasswordRegistration = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    if (form.password !== form.confirmPassword) {
      setError('Passwords do not match');
      setIsLoading(false);
      return;
    }
    const passwordError = getPasswordError(form.password);
    if (passwordError) {
      setError(passwordError);
      setIsLoading(false);
      return;
    }
    try {
      const email = `${form.phoneNumber}@phone.com`;
      const userCredential = await createUserWithEmailAndPassword(auth, email, form.password);
      const idToken = await userCredential.user.getIdToken();
      const backendUser = await import('@/lib/auth').then(m => m.registerUserBackend(idToken, form.phoneNumber));
      localStorage.setItem('userRole', backendUser.role?.toLowerCase?.() || 'user');
      if (backendUser.role === 'Admin') {
        router.push('/admin/products');
      } else {
        router.push('/');
      }
    } catch (error: any) {
      setError(error.message || 'Registration failed');
    } finally {
      setIsLoading(false);
    }
  };

  const onSubmit = (e: React.FormEvent) => {
    handlePasswordRegistration(e);
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
            isInvalid={!!getPasswordError(form.password) && form.password.length > 0}
            errorMessage={form.password.length > 0 ? getPasswordError(form.password) : undefined}
          />
          <Input
            label="Confirm Password"
            labelPlacement="outside"
            classNames={{ label: 'mb-2' }}
            placeholder="Confirm your password"
            type="password"
            value={form.confirmPassword}
            onValueChange={val => setForm(f => ({ ...f, confirmPassword: val }))}
            isInvalid={form.password !== form.confirmPassword && form.confirmPassword.length > 0}
            errorMessage={form.password !== form.confirmPassword && form.confirmPassword.length > 0 ? 'Passwords do not match' : undefined}
          />
          <Button
            type="submit"
            color="primary"
            className="w-full"
            isLoading={isLoading}
          >
            Register
          </Button>
          <Button
            type="button"
            variant="bordered"
            className="w-full"
            onPress={onSwitchToLogin}
          >
            Already have an account? Login
          </Button>
        </div>
      </Form>
    </div>
  );
} 