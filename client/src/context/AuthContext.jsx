// client/src/context/AuthContext.jsx
import { createContext, useState, useEffect, useMemo, useCallback } from 'react';
import { getCurrentUser } from '../api/user';
import { getToken, clearToken } from '../utils/token';
import { logoutUser, logoutAllDevices, emergencyLogout } from '../api/auth-logout';

// Initial context to avoid undefined errors
export const AuthContext = createContext({
  user: null,
  setUser: () => {},
  logout: () => {},
  logoutAll: () => {},
  emergencyLogout: () => {},
  loading: true,
});

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Standard logout - revoke current session
  const logout = useCallback(async () => {
    setLoading(true);
    try {
      await logoutUser();
      setUser(null);
    } catch (error) {
      console.error('❌ Logout failed:', error);
      // Force local cleanup even if server fails
      clearToken();
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  // Logout from all devices
  const logoutAll = useCallback(async () => {
    setLoading(true);
    try {
      await logoutAllDevices();
      setUser(null);
    } catch (error) {
      console.error('❌ Logout all failed:', error);
      // Force local cleanup even if server fails
      clearToken();
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  // Emergency logout - immediate local cleanup
  const handleEmergencyLogout = useCallback(() => {
    emergencyLogout();
    setUser(null);
    setLoading(false);
  }, []);

  useEffect(() => {
    const initializeUser = async () => {
      const token = getToken();
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const currentUser = await getCurrentUser();
        setUser(currentUser);
      } catch (err) {
        console.warn('⚠️ Auto-login failed:', err.message);
        // Use emergency logout for initialization failures
        clearToken();
        setUser(null);
        setLoading(false);
      } finally {
        setLoading(false);
      }
    };

    initializeUser();
  }, []); // Remove dependency to prevent infinite loop

  // Memoize the context value to prevent infinite re-renders
  const contextValue = useMemo(() => ({
    user,
    setUser,
    logout,
    logoutAll,
    emergencyLogout: handleEmergencyLogout,
    loading,
    isAuthenticated: !!user, // Add this computed property
    isLoading: loading, // Add alias for backward compatibility
  }), [user, logout, logoutAll, handleEmergencyLogout, loading]);

  return (
    <AuthContext.Provider value={contextValue}>
      {loading ? (
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-2 text-sm text-gray-600">Loading...</p>
          </div>
        </div>
      ) : (
        children
      )}
    </AuthContext.Provider>
  );
};
