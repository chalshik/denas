'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { createUserWithEmailAndPassword } from 'firebase/auth';
import { auth } from '@/lib/firebase';
import { Form } from '@heroui/form';
import { Input } from '@heroui/input';
import { Button } from '@heroui/button';

export default function RegisterForm() {
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setErrors({});
    const formData = new FormData(e.currentTarget);
    const phone = formData.get('phone') as string;
    const password = formData.get('password') as string;
    const repeatPassword = formData.get('repeatPassword') as string;
    if (password !== repeatPassword) {
      setErrors({ repeatPassword: 'Passwords do not match' });
      setLoading(false);
      return;
    }
    if (password.length < 6) {
      setErrors({ password: 'Password must be at least 6 characters long' });
      setLoading(false);
      return;
    }
    const email = `${phone}@example.com`;
    try {
      await createUserWithEmailAndPassword(auth, email, password);
      router.push('/');
    } catch (error: any) {
      setErrors({
        phone: error.code === 'auth/email-already-in-use'
          ? 'An account with this phone number already exists'
          : 'An error occurred during registration',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md mx-auto bg-white p-8 rounded-xl shadow">
      <Form
        className="flex flex-col gap-6"
        validationErrors={errors}
        onSubmit={handleSubmit}
      >
        <div>
          <label htmlFor="phone" className="block mb-2 text-sm font-medium text-gray-700">
            Phone Number<span className="text-red-500">*</span>
          </label>
          <Input
            id="phone"
            name="phone"
            type="tel"
            required
            placeholder="Enter your phone number"
            className="w-full rounded-lg border border-gray-300 bg-gray-100 px-4 py-2 focus:border-blue-500 focus:bg-white focus:outline-none transition"
          />
        </div>
        <div>
          <label htmlFor="password" className="block mb-2 text-sm font-medium text-gray-700">
            Password<span className="text-red-500">*</span>
          </label>
          <Input
            id="password"
            name="password"
            type="password"
            required
            placeholder="Enter your password"
            className="w-full rounded-lg border border-gray-300 bg-gray-100 px-4 py-2 focus:border-blue-500 focus:bg-white focus:outline-none transition"
          />
        </div>
        <div>
          <label htmlFor="repeatPassword" className="block mb-2 text-sm font-medium text-gray-700">
            Repeat Password<span className="text-red-500">*</span>
          </label>
          <Input
            id="repeatPassword"
            name="repeatPassword"
            type="password"
            required
            placeholder="Repeat your password"
            className="w-full rounded-lg border border-gray-300 bg-gray-100 px-4 py-2 focus:border-blue-500 focus:bg-white focus:outline-none transition"
          />
        </div>
        <Button
          type="submit"
          className="w-full h-10 rounded-lg bg-blue-600 text-white font-semibold hover:bg-blue-700 transition"
          isLoading={loading}
          disabled={loading}
        >
          Register
        </Button>
      </Form>
    </div>
  );
} 