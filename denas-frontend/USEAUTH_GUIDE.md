# useAuth Hook - Руководство по использованию

## 🎯 **Обзор**

Хук `useAuth` предоставляет централизованный способ управления аутентификацией в приложении. Он объединяет состояние пользователя, роль и методы аутентификации в одном месте.

## 📁 **Структура файлов**

```
app/hooks/
└── useAuth.ts          # Основной хук аутентификации

components/auth/
└── ProtectedRoute.tsx  # Компонент для защищенных маршрутов

lib/
├── firebase.ts         # Конфигурация Firebase
└── auth.ts            # Утилиты для работы с ролями
```

## 🪝 **Основной хук useAuth**

### **Возвращаемые значения**

```typescript
interface AuthState {
  user: User | null; // Объект пользователя Firebase
  role: "admin" | "user" | null; // Роль пользователя
  loading: boolean; // Состояние загрузки
  isAuthenticated: boolean; // Авторизован ли пользователь
  isAdmin: boolean; // Является ли админом
}

interface AuthActions {
  logout: () => Promise<void>; // Выход из системы
  setUserRole: (role: "admin" | "user") => void; // Установка роли
  clearUserRole: () => void; // Очистка роли
}
```

### **Пример использования**

```typescript
import { useAuth } from '@/app/hooks/useAuth';

function MyComponent() {
  const {
    user,
    role,
    loading,
    isAuthenticated,
    isAdmin,
    logout
  } = useAuth();

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!isAuthenticated) {
    return <div>Please log in</div>;
  }

  return (
    <div>
      <p>Welcome, {user?.email}</p>
      <p>Role: {role}</p>
      {isAdmin && <p>You are an admin!</p>}
      <button onClick={logout}>Logout</button>
    </div>
  );
}
```

## 🔐 **Специализированные хуки**

### **useAdminAccess()**

Проверяет доступ к админ-функциям:

```typescript
import { useAdminAccess } from '@/app/hooks/useAuth';

function AdminComponent() {
  const { canAccess, loading, isAuthenticated, isAdmin } = useAdminAccess();

  if (loading) return <div>Loading...</div>;
  if (!canAccess) return <div>Access denied</div>;

  return <div>Admin content</div>;
}
```

### **useProtectedRoute(requireAdmin)**

Для защищенных маршрутов:

```typescript
import { useProtectedRoute } from '@/app/hooks/useAuth';

function ProtectedComponent() {
  const { user, canAccess, loading } = useProtectedRoute(true); // requireAdmin = true

  if (loading) return <div>Loading...</div>;
  if (!canAccess) return <div>Access denied</div>;

  return <div>Protected content</div>;
}
```

## 🛡️ **Компоненты защищенных маршрутов**

### **ProtectedRoute**

Основной компонент для защиты маршрутов:

```typescript
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';

function AdminPage() {
  return (
    <ProtectedRoute requireAdmin>
      <div>Admin content</div>
    </ProtectedRoute>
  );
}
```

### **AdminRoute**

Удобный компонент для админ-страниц:

```typescript
import { AdminRoute } from '@/components/auth/ProtectedRoute';

function AdminPage() {
  return (
    <AdminRoute>
      <div>Admin content</div>
    </AdminRoute>
  );
}
```

### **AuthRoute**

Для авторизованных пользователей:

```typescript
import { AuthRoute } from '@/components/auth/ProtectedRoute';

function UserPage() {
  return (
    <AuthRoute>
      <div>User content</div>
    </AuthRoute>
  );
}
```

## 🔄 **Интеграция с формами аутентификации**

### **Обновление LoginForm**

```typescript
import { useAuth } from "@/app/hooks/useAuth";

function LoginForm() {
  const { setUserRole } = useAuth();

  const handleLogin = async () => {
    // ... логика входа
    const isAdmin = phoneNumber.includes("admin");
    setUserRole(isAdmin ? "admin" : "user");
  };
}
```

### **Обновление RegisterForm**

```typescript
import { useAuth } from "@/app/hooks/useAuth";

function RegisterForm() {
  const { setUserRole } = useAuth();

  const handleRegister = async () => {
    // ... логика регистрации
    const isAdmin = phoneNumber.includes("admin");
    setUserRole(isAdmin ? "admin" : "user");
  };
}
```

## 🎯 **Примеры использования в компонентах**

### **Navbar с аутентификацией**

```typescript
import { useAuth } from '@/app/hooks/useAuth';

function Navbar() {
  const { user, isAdmin, logout } = useAuth();

  return (
    <nav>
      {user ? (
        <>
          {isAdmin && <Link href="/admin">Admin Panel</Link>}
          <button onClick={logout}>Logout</button>
        </>
      ) : (
        <Link href="/auth/login">Login</Link>
      )}
    </nav>
  );
}
```

### **Защищенная страница**

```typescript
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';

function UserProfile() {
  return (
    <ProtectedRoute>
      <div>User profile content</div>
    </ProtectedRoute>
  );
}
```

### **Админ-страница**

```typescript
import { AdminRoute } from '@/components/auth/ProtectedRoute';

function AdminDashboard() {
  return (
    <AdminRoute>
      <div>Admin dashboard content</div>
    </AdminRoute>
  );
}
```

## 🚀 **Преимущества использования**

### **1. Централизованное управление**

- Все состояние аутентификации в одном месте
- Легко отслеживать изменения
- Простое тестирование

### **2. Типобезопасность**

- Полная типизация TypeScript
- Автодополнение в IDE
- Предотвращение ошибок

### **3. Переиспользование**

- Один хук для всего приложения
- Консистентное поведение
- Легкое обновление логики

### **4. Производительность**

- Оптимизированные ре-рендеры
- Кэширование состояния
- Эффективные обновления

## 🔧 **Настройка для продакшена**

### **Интеграция с API**

```typescript
// В useAuth.ts
const checkUserRole = async (uid: string) => {
  const response = await fetch(`/api/users/${uid}/role`);
  const { role } = await response.json();
  return role;
};
```

### **JWT токены**

```typescript
// В useAuth.ts
const getAuthToken = () => {
  return localStorage.getItem("authToken");
};

const setAuthToken = (token: string) => {
  localStorage.setItem("authToken", token);
};
```

### **Middleware для API**

```typescript
// middleware.ts
export function middleware(request: NextRequest) {
  const token = request.headers.get("authorization");
  // Проверка токена и роли
}
```

## 📝 **Лучшие практики**

1. **Всегда проверяйте loading состояние**
2. **Используйте ProtectedRoute для защищенных страниц**
3. **Обрабатывайте ошибки аутентификации**
4. **Кэшируйте состояние пользователя**
5. **Логируйте важные действия**

## 🎯 **Тестирование**

```typescript
// test/useAuth.test.ts
import { renderHook } from "@testing-library/react";
import { useAuth } from "@/app/hooks/useAuth";

test("should return correct auth state", () => {
  const { result } = renderHook(() => useAuth());

  expect(result.current.loading).toBe(true);
  expect(result.current.isAuthenticated).toBe(false);
});
```
