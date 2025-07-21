# Firebase Setup Guide

## Environment Variables

Create a `.env.local` file in the root of your project with the following Firebase configuration:

```env
# Firebase Configuration
# Replace these values with your actual Firebase project credentials
NEXT_PUBLIC_FIREBASE_API_KEY=your_api_key_here
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_project_id.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_project_id.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_messaging_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
```

## Getting Firebase Credentials

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project or select an existing one
3. Go to Project Settings (gear icon)
4. Scroll down to "Your apps" section
5. Click "Add app" and select "Web"
6. Register your app and copy the configuration values
7. Replace the placeholder values in `.env.local` with your actual Firebase credentials

## Firebase Authentication Setup

1. In Firebase Console, go to Authentication
2. Click "Get started"
3. Enable the following sign-in methods:
   - Phone (for phone number authentication)
   - Email/Password (for password authentication)
4. Configure the phone authentication settings as needed

## Features

The authentication system supports:

- **Phone Number Authentication**: Users can sign in/up with their phone number and receive SMS verification codes
- **Password Authentication**: Users can create accounts with phone number + password combination
- **Real-time validation**: Password strength validation and form validation
- **Error handling**: Comprehensive error messages for various authentication scenarios
- **Responsive design**: Works on all device sizes
- **Hero UI components**: Modern, accessible UI components

## Usage

- Login page: `/auth/login`
- Register page: `/auth/register`
- After successful authentication, users are redirected to `/`
