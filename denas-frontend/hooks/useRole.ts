import { useAuth } from '@/contexts/AuthContext';
import { UserRole, RolePermissions } from '@/types/auth';

export const useRole = () => {
  const { user } = useAuth();

  const hasRole = (role: UserRole): boolean => {
    return user?.role === role;
  };

  const hasAdminAccess = (): boolean => {
    return user?.role === UserRole.ADMIN || user?.role === UserRole.MANAGER;
  };

  const isAdmin = (): boolean => {
    return user?.role === UserRole.ADMIN;
  };

  const isManager = (): boolean => {
    return user?.role === UserRole.MANAGER;
  };

  const isUser = (): boolean => {
    return user?.role === UserRole.USER;
  };

  const getPermissions = (): RolePermissions => {
    const basePermissions: RolePermissions = {
      canViewAdmin: false,
      canManageUsers: false,
      canViewStats: false,
      canUpdateRoles: false,
      canDeleteUsers: false,
    };

    if (!user) return basePermissions;

    switch (user.role) {
      case UserRole.ADMIN:
        return {
          canViewAdmin: true,
          canManageUsers: true,
          canViewStats: true,
          canUpdateRoles: true,
          canDeleteUsers: true,
        };
      case UserRole.MANAGER:
        return {
          canViewAdmin: true,
          canManageUsers: true,
          canViewStats: true,
          canUpdateRoles: false,
          canDeleteUsers: false,
        };
      default:
        return basePermissions;
    }
  };

  const canAccess = (permission: keyof RolePermissions): boolean => {
    return getPermissions()[permission];
  };

  return {
    user,
    hasRole,
    hasAdminAccess,
    isAdmin,
    isManager,
    isUser,
    getPermissions,
    canAccess,
    currentRole: user?.role,
  };
}; 