'use client';

import React from 'react';
import { useRole } from '@/hooks/useRole';
import { UserRole, RolePermissions } from '@/types/auth';
import { Card, CardBody, Button } from '@heroui/react';
import { Shield, AlertTriangle } from 'lucide-react';

interface RoleGuardProps {
  children: React.ReactNode;
  requiredRole?: UserRole;
  requiredPermission?: keyof RolePermissions;
  fallback?: React.ReactNode;
  showFallback?: boolean;
}

export const RoleGuard: React.FC<RoleGuardProps> = ({
  children,
  requiredRole,
  requiredPermission,
  fallback,
  showFallback = true,
}) => {
  const { hasRole, canAccess, user } = useRole();

  const hasAccess = () => {
    if (!user) return false;
    
    if (requiredRole && !hasRole(requiredRole)) {
      return false;
    }
    
    if (requiredPermission && !canAccess(requiredPermission)) {
      return false;
    }
    
    return true;
  };

  if (!hasAccess()) {
    if (fallback) {
      return <>{fallback}</>;
    }
    
    if (!showFallback) {
      return null;
    }
    
    return (
      <Card className="max-w-md mx-auto border-red-200 bg-red-50">
        <CardBody className="text-center py-8">
          <AlertTriangle className="h-12 w-12 text-red-600 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-red-800 mb-2">
            Access Denied
          </h3>
          <p className="text-red-600 mb-4">
            You don't have permission to access this resource.
          </p>
          {requiredRole && (
            <p className="text-sm text-red-500">
              Required role: {requiredRole}
            </p>
          )}
          {requiredPermission && (
            <p className="text-sm text-red-500">
              Required permission: {requiredPermission}
            </p>
          )}
        </CardBody>
      </Card>
    );
  }

  return <>{children}</>;
};

// Convenience components for common cases
export const AdminOnly: React.FC<{ children: React.ReactNode; fallback?: React.ReactNode }> = ({
  children,
  fallback,
}) => (
  <RoleGuard requiredRole={UserRole.ADMIN} fallback={fallback}>
    {children}
  </RoleGuard>
);

export const AdminOrManager: React.FC<{ children: React.ReactNode; fallback?: React.ReactNode }> = ({
  children,
  fallback,
}) => (
  <RoleGuard requiredPermission="canViewAdmin" fallback={fallback}>
    {children}
  </RoleGuard>
);

export const UserOnly: React.FC<{ children: React.ReactNode; fallback?: React.ReactNode }> = ({
  children,
  fallback,
}) => (
  <RoleGuard requiredRole={UserRole.USER} fallback={fallback}>
    {children}
  </RoleGuard>
);

export default RoleGuard; 