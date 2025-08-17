import { useEffect, useState } from 'react';
import useAuth from '../hooks/useAuth';
import { useNavigate } from 'react-router-dom';

export default function Logout() {
  const { logout, logoutAll, emergencyLogout } = useAuth();
  const navigate = useNavigate();
  const [logoutType, setLogoutType] = useState('normal');
  const [error, setError] = useState(null);

  useEffect(() => {
    const performLogout = async () => {
      try {
        // Check if emergency logout is needed (e.g., from URL params)
        const urlParams = new URLSearchParams(window.location.search);
        const isEmergency = urlParams.get('emergency') === 'true';
        const isLogoutAll = urlParams.get('all') === 'true';

        if (isEmergency) {
          setLogoutType('emergency');
          emergencyLogout();
        } else if (isLogoutAll) {
          setLogoutType('all');
          await logoutAll();
        } else {
          setLogoutType('normal');
          await logout();
        }

        // Redirect after successful logout
        setTimeout(() => {
          navigate('/', { replace: true });
        }, 2000);

      } catch (err) {
        console.error('Logout failed:', err);
        setError(err.message);
        
        // If normal logout fails, try emergency logout
        if (logoutType === 'normal') {
          setLogoutType('emergency');
          emergencyLogout();
          setTimeout(() => {
            navigate('/', { replace: true });
          }, 1000);
        }
      }
    };

    performLogout();
  }, [logout, logoutAll, emergencyLogout, navigate]);

  const getLogoutMessage = () => {
    switch (logoutType) {
      case 'emergency':
        return 'Emergency logout...';
      case 'all':
        return 'Logging out from all devices...';
      default:
        return 'Logging out...';
    }
  };

  const getLogoutDescription = () => {
    switch (logoutType) {
      case 'emergency':
        return 'Clearing all local data immediately';
      case 'all':
        return 'Revoking all tokens across devices';
      default:
        return 'Ending your current session';
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-white dark:bg-gray-900 text-gray-800 dark:text-white">
      <div className="text-center space-y-4 max-w-md mx-auto p-6">
        {error ? (
          <div className="space-y-4">
            <div className="w-12 h-12 mx-auto text-red-500">
              <svg fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div>
              <p className="text-lg font-medium text-red-600">Logout Failed</p>
              <p className="text-sm text-gray-600 mt-2">{error}</p>
              <p className="text-xs text-gray-500 mt-2">Performing emergency cleanup...</p>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-blue-600 mx-auto"></div>
            <div>
              <p className="text-lg font-medium">{getLogoutMessage()}</p>
              <p className="text-sm text-gray-600 mt-2">{getLogoutDescription()}</p>
            </div>
          </div>
        )}
        
        <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
          <p className="text-xs text-gray-500">
            You will be redirected to the homepage...
          </p>
        </div>
      </div>
    </div>
  );
}
