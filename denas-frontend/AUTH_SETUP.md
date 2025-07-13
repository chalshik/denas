# Authentication Setup

This project uses Firebase Authentication for user login and registration.

## Environment Variables

Create a `.env` file in the root directory with the following Firebase configuration:

```env
NEXT_PUBLIC_FIREBASE_API_KEY=your_api_key_here
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_project_id.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_project_id.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
```

## Features

- **Login**: Email and password authentication
- **Registration**: Create new accounts with email and password
- **Form Validation**: Client-side validation for passwords and email
- **Error Handling**: User-friendly error messages
- **Loading States**: Loading indicators during authentication
- **Responsive Design**: Mobile-friendly UI using Hero UI components

## File Structure

```
app/
├── auth/
│   ├── layout.tsx          # Auth layout wrapper
│   ├── login/
│   │   └── page.tsx        # Login page
│   └── register/
│       └── page.tsx        # Register page

components/
└── forms/
    ├── LoginForm.tsx       # Reusable login form
    └── RegisterForm.tsx    # Reusable register form

lib/
├── firebase.ts             # Firebase configuration
└── auth.ts                 # Authentication utilities
```

## Usage

1. Navigate to `/auth/login` to sign in
2. Navigate to `/auth/register` to create a new account
3. After successful authentication, users are redirected to `/`

## Components

### LoginForm
- Email and password fields
- Form validation
- Error message display
- Loading state during authentication

### RegisterForm
- Email, password, and confirm password fields
- Password confirmation validation
- Minimum password length validation
- Error message display
- Loading state during registration

## Authentication Hook

Use the `useAuth` hook to access the current user:

```tsx
import { useAuth } from '@/lib/auth';

function MyComponent() {
  const { user, loading } = useAuth();
  
  if (loading) return <div>Loading...</div>;
  
  return user ? <div>Welcome, {user.email}</div> : <div>Please sign in</div>;
}
``` 