// Layout
export { default as AdminLayout } from './layout/AdminLayout';

// Products
export { default as ProductsManagement } from './products/ProductsManagement';

// Chat
export { default as ChatManagement } from './chat/ChatManagement';

// Analytics  
export { default as AnalyticsManagement } from './analytics/AnalyticsManagement';

// Settings
export { default as SettingsManagement } from './settings/SettingsManagement';

// Dashboard
export { default as AdminDashboard } from './dashboard/AdminDashboard';
export { default as StatsCards } from './dashboard/StatsCards';
export { default as RecentUsers } from './dashboard/RecentUsers';
export { default as RoleDistribution } from './dashboard/RoleDistribution';

// Guards
export { default as RoleGuard, AdminOnly, AdminOrManager, UserOnly } from '../auth/RoleGuard'; 