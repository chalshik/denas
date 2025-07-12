# Настройка аутентификации Firebase

## Шаг 1: Настройка Firebase проекта

1. Создайте проект в [Firebase Console](https://console.firebase.google.com/)
2. Включите Authentication -> Sign-in method -> Email/Password
3. Скопируйте конфигурацию Firebase

## Шаг 2: Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```env
# Firebase Configuration
NEXT_PUBLIC_FIREBASE_API_KEY=your_api_key_here
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_project_id.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_project_id.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id

# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## Шаг 3: Запуск приложения

```bash
npm run dev
```

## Как работает аутентификация

1. **Ввод номера телефона и пароля** - пользователь вводит номер телефона и пароль
2. **Регистрация или вход** - пользователь выбирает регистрацию или вход
3. **Firebase аутентификация** - Firebase проверяет учетные данные
4. **Регистрация в бэкенде** - для новых пользователей создается запись в базе данных
5. **Авторизация** - пользователь получает доступ к приложению

## Особенности реализации

- Номер телефона конвертируется в email формат для Firebase (например: `1234567890@phone.auth`)
- Firebase используется только для аутентификации, все пользовательские данные хранятся в бэкенде
- Минимальная длина пароля: 6 символов

## Структура файлов

- `lib/firebase.ts` - конфигурация Firebase и вспомогательные функции
- `lib/api.ts` - API клиент для связи с бэкендом
- `contexts/AuthContext.tsx` - контекст для управления состоянием аутентификации
- `components/auth/PhoneAuth.tsx` - компонент для аутентификации по номеру телефона и паролю
- `components/auth/UserProfile.tsx` - компонент для отображения профиля пользователя

## Требования к бэкенду

Бэкенд должен предоставлять следующие API эндпоинты:

- `POST /auth/register` - регистрация нового пользователя
- `GET /auth/me` - получение текущего пользователя
- `GET /auth/me/or-create` - получение пользователя или создание нового

Все запросы должны включать Firebase JWT токен в заголовке Authorization. 