export enum UserRole {
  USER = 'User',
  ADMIN = 'Admin',
  MANAGER = 'Manager'
}

export interface User {
  id: number;
  uid: string;
  phone: string;
  role: UserRole;
  created_at: string;
}

export interface AuthContextType {
  user: User | null;
  firebaseUser: any | null;
  loading: boolean;
  error: string | null;
  signOut: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

export interface UserStats {
  total_users: number;
  users_by_role: {
    [UserRole.USER]: number;
    [UserRole.ADMIN]: number;
    [UserRole.MANAGER]: number;
  };
  users_today: number;
  users_this_week: number;
  users_this_month: number;
}

export interface UserListResponse {
  users: User[];
  total_count: number;
  page: number;
  limit: number;
  has_next: boolean;
  has_previous: boolean;
}

export interface RolePermissions {
  canViewAdmin: boolean;
  canManageUsers: boolean;
  canViewStats: boolean;
  canUpdateRoles: boolean;
  canDeleteUsers: boolean;
} 