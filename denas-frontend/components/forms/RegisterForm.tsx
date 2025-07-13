'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { createUserWithEmailAndPassword, signInWithPhoneNumber, RecaptchaVerifier } from 'firebase/auth';
import { auth } from '@/lib/firebase';
import { Button } from '@heroui/button';
import { Input } from '@heroui/input';
import { Form } from '@heroui/form';

interface RegisterFormProps {
  onSwitchToLogin?: () => void;
}

export default function RegisterForm({ onSwitchToLogin }: RegisterFormProps) {
  const [phoneNumber, setPhoneNumber] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [verificationCode, setVerificationCode] = useState('');
  const [showVerification, setShowVerification] = useState(false);
  const [confirmationResult, setConfirmationResult] = useState<any>(null);
  
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

  const handlePhoneRegistration = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    // Validate passwords match
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      setIsLoading(false);
      return;
    }

    // Validate password strength
    const passwordError = getPasswordError(password);
    if (passwordError) {
      setError(passwordError);
      setIsLoading(false);
      return;
    }

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

  const handlePasswordRegistration = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    // Validate passwords match
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      setIsLoading(false);
      return;
    }

    // Validate password strength
    const passwordError = getPasswordError(password);
    if (passwordError) {
      setError(passwordError);
      setIsLoading(false);
      return;
    }

    try {
      // For password registration, we'll use email format with phone number
      const email = `${phoneNumber}@phone.com`;
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      const idToken = await userCredential.user.getIdToken();
      // Зарегистрировать пользователя на бэке
      const backendUser = await import('@/lib/auth').then(m => m.registerUserBackend(idToken, phoneNumber));
      // Сохраняем роль (например, в localStorage или context)
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
    if (showVerification) {
      handleVerifyCode(e);
    } else if (password) {
      handlePasswordRegistration(e);
    } else {
      handlePhoneRegistration(e);
    }
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
            value={phoneNumber}
            onValueChange={setPhoneNumber}
            isInvalid={!!error && !showVerification}
            errorMessage={error && !showVerification ? error : undefined}
          />

          {!showVerification && (
            <>
              <Input
                label="Password"
                labelPlacement="outside"
                classNames={{ label: 'mb-2' }}
                placeholder="Enter your password"
                type="password"
                value={password}
                onValueChange={setPassword}
                isInvalid={!!getPasswordError(password) && password.length > 0}
                errorMessage={password.length > 0 ? getPasswordError(password) : undefined}
              />

              <Input
                label="Confirm Password"
                labelPlacement="outside"
                classNames={{ label: 'mb-2' }}
                placeholder="Confirm your password"
                type="password"
                value={confirmPassword}
                onValueChange={setConfirmPassword}
                isInvalid={password !== confirmPassword && confirmPassword.length > 0}
                errorMessage={password !== confirmPassword && confirmPassword.length > 0 ? 'Passwords do not match' : undefined}
              />
            </>
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
            {showVerification ? 'Verify Code' : 'Register'}
          </Button>

          {!showVerification && (
            <Button
              type="button"
              variant="bordered"
              className="w-full"
              onPress={onSwitchToLogin}
            >
              Already have an account? Login
            </Button>
          )}
        </div>
      </Form>
    </div>
  );
} 