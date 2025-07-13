'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { signInWithEmailAndPassword, signInWithPhoneNumber, RecaptchaVerifier } from 'firebase/auth';
import { auth } from '@/lib/firebase';
import { Button } from '@heroui/button';
import { Input } from '@heroui/input';
import { Form } from '@heroui/form';

interface LoginFormProps {
  onSwitchToRegister?: () => void;
}

export default function LoginForm({ onSwitchToRegister }: LoginFormProps) {
  const [phoneNumber, setPhoneNumber] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [verificationCode, setVerificationCode] = useState('');
  const [showVerification, setShowVerification] = useState(false);
  const [confirmationResult, setConfirmationResult] = useState<any>(null);
  
  const router = useRouter();

  const handlePhoneLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      // Create recaptcha verifier
      const recaptchaVerifier = new RecaptchaVerifier(auth, 'recaptcha-container', {
        'size': 'normal',
        'callback': () => {
          // reCAPTCHA solved, allow sending SMS.
        }
      });

      // Send SMS
      const formattedPhone = phoneNumber.startsWith('+') ? phoneNumber : `+${phoneNumber}`;
      const confirmation = await signInWithPhoneNumber(auth, formattedPhone, recaptchaVerifier);
      setConfirmationResult(confirmation);
      setShowVerification(true);
    } catch (error: any) {
      setError(error.message || 'Failed to send verification code');
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerifyCode = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      await confirmationResult.confirm(verificationCode);
      router.push('/');
    } catch (error: any) {
      setError('Invalid verification code');
    } finally {
      setIsLoading(false);
    }
  };

  const handlePasswordLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      // For password login, we'll use email format with phone number
      const email = `${phoneNumber}@phone.com`;
      await signInWithEmailAndPassword(auth, email, password);
      
      // Check if user is admin (this should come from your backend)
      // For demo purposes, we'll check if phone number contains 'admin'
      const isAdmin = phoneNumber.includes('admin') || phoneNumber === '+1234567890';
      localStorage.setItem('userRole', isAdmin ? 'admin' : 'user');
      
      if (isAdmin) {
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
    if (showVerification) {
      handleVerifyCode(e);
    } else if (password) {
      handlePasswordLogin(e);
    } else {
      handlePhoneLogin(e);
    }
  };

  return (
    <div className="w-full max-w-md mx-auto">
      <Form
        className="w-full space-y-4"
        onSubmit={onSubmit}
      >
        <div className="space-y-4">
          <Input
            isRequired
            label="Phone Number"
            labelPlacement="outside"
            placeholder="+1234567890"
            value={phoneNumber}
            onValueChange={setPhoneNumber}
            isInvalid={!!error && !showVerification}
            errorMessage={error && !showVerification ? error : undefined}
          />

          {!showVerification && (
            <Input
              label="Password (optional)"
              labelPlacement="outside"
              placeholder="Enter your password"
              type="password"
              value={password}
              onValueChange={setPassword}
            />
          )}

          {!showVerification && !password && (
            <div id="recaptcha-container" className="mt-4"></div>
          )}

          {showVerification && (
            <Input
              isRequired
              label="Verification Code"
              labelPlacement="outside"
              placeholder="Enter 6-digit code"
              value={verificationCode}
              onValueChange={setVerificationCode}
              isInvalid={!!error}
              errorMessage={error}
            />
          )}

          <Button
            type="submit"
            color="primary"
            className="w-full"
            isLoading={isLoading}
          >
            {showVerification ? 'Verify Code' : 'Login'}
          </Button>

          {!showVerification && (
            <Button
              type="button"
              variant="bordered"
              className="w-full"
              onPress={onSwitchToRegister}
            >
              Don't have an account? Register
            </Button>
          )}
        </div>
      </Form>
    </div>
  );
} 