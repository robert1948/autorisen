import { Navigate, useLocation } from 'react-router-dom';
import { useMemo } from 'react';
import useAuth from '../hooks/useAuth';

export default function ProtectedRoute({ children, requiredRole = null }) {
  const { user, loading } = useAuth();
  const location = useLocation();

  // Memoize computations to prevent unnecessary re-renders
  const dashboardRedirect = useMemo(() => {
    if (!user?.role) return '/dashboard/user';
    return getRoleBasedDashboard(user.role);
  }, [user?.role]);

  const isAuthorized = useMemo(() => {
    if (!requiredRole || !user?.role) return true;
    return isRoleCompatible(user.role, requiredRole);
  }, [user?.role, requiredRole]);

  // Show loading if authentication is still in progress
  if (loading || user === undefined) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-sm text-gray-600">Checking authentication...</p>
        </div>
      </div>
    );
  }

  // If user is not logged in (null), redirect to login
  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Check if a specific role is required
  if (requiredRole && !isAuthorized) {
    // Redirect to appropriate dashboard based on user's actual role
    return <Navigate to={dashboardRedirect} replace />;
  }

  // If accessing /dashboard root, redirect to role-specific dashboard
  if (location.pathname === '/dashboard' && user.role) {
    return <Navigate to={dashboardRedirect} replace />;
  }

  // Authenticated and authorized → allow access
  return children;
}

// Helper function to get role-based dashboard route
function getRoleBasedDashboard(userRole) {
  const roleRouteMap = {
    // Frontend role names
    'client': '/dashboard/user',
    'customer': '/dashboard/user', 
    'developer': '/dashboard/developer',
    'admin': '/dashboard/performance',
    
    // Backend role names (uppercase)
    'CUSTOMER': '/dashboard/user',
    'DEVELOPER': '/dashboard/developer', 
    'ADMIN': '/dashboard/performance',
    
    // Legacy compatibility
    'business_user': '/dashboard/user',
    'analyst': '/dashboard/user',
    'manager': '/dashboard/performance'
  };

  return roleRouteMap[userRole] || '/dashboard/user';
}

// Helper function to check role compatibility
export function isRoleCompatible(userRole, requiredRole) {
  const normalizedUserRole = normalizeRole(userRole);
  const normalizedRequiredRole = normalizeRole(requiredRole);
  
  return normalizedUserRole === normalizedRequiredRole;
}

function normalizeRole(role) {
  const roleMap = {
    'client': 'customer',
    'customer': 'customer',
    'CUSTOMER': 'customer',
    'business_user': 'customer',
    'analyst': 'customer',
    
    'developer': 'developer',
    'DEVELOPER': 'developer',
    
    'admin': 'admin',
    'ADMIN': 'admin',
    'manager': 'admin'
  };
  
  return roleMap[role] || 'customer';
}
