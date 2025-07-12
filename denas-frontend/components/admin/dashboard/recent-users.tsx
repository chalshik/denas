'use client';

import React from 'react';
import { 
  Card, 
  CardHeader, 
  CardBody,
  Table,
  TableHeader,
  TableColumn,
  TableBody,
  TableRow,
  TableCell,
  Chip,
  Button
} from '@heroui/react';
import { RefreshCw } from 'lucide-react';
import { User, UserRole } from '@/types/auth';

interface RecentUsersProps {
  users: User[];
  onRefresh: () => void;
}

const RecentUsers: React.FC<RecentUsersProps> = ({ users, onRefresh }) => {
  const getRoleColor = (role: UserRole) => {
    switch (role) {
      case UserRole.ADMIN:
        return 'danger';
      case UserRole.MANAGER:
        return 'warning';
      case UserRole.USER:
        return 'primary';
      default:
        return 'default';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <Card>
      <CardHeader className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Recent Users</h3>
        <Button
          color="primary"
          variant="light"
          size="sm"
          startContent={<RefreshCw className="h-4 w-4" />}
          onPress={onRefresh}
        >
          Refresh
        </Button>
      </CardHeader>
      <CardBody>
        {users.length > 0 ? (
          <Table aria-label="Recent users table">
            <TableHeader>
              <TableColumn>ID</TableColumn>
              <TableColumn>Phone</TableColumn>
              <TableColumn>Role</TableColumn>
              <TableColumn>Created</TableColumn>
            </TableHeader>
            <TableBody>
              {users.map((user) => (
                <TableRow key={user.id}>
                  <TableCell className="font-mono text-sm">
                    #{user.id}
                  </TableCell>
                  <TableCell className="font-medium">
                    {user.phone}
                  </TableCell>
                  <TableCell>
                    <Chip
                      color={getRoleColor(user.role)}
                      size="sm"
                      variant="flat"
                    >
                      {user.role}
                    </Chip>
                  </TableCell>
                  <TableCell className="text-sm text-gray-600">
                    {formatDate(user.created_at)}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        ) : (
          <div className="text-center py-8">
            <p className="text-gray-500">No users found</p>
          </div>
        )}
      </CardBody>
    </Card>
  );
};

export default RecentUsers; 