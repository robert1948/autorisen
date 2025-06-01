import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { jwtDecode } from 'jwt-decode';

const RequireAuth = ({ children }) => {
  const { token, logout } = useAuth();
  const location = useLocation();

  if (!token) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  try {
    const decoded = jwtDecode(token);
    const now = Date.now() / 1000;

    if (decoded.exp < now) {
      logout(); // Token expired
      return <Navigate to="/login" state={{ from: location }} replace />;
    }

    return children;
  } catch (error) {
    logout(); // Invalid token
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
};

export default RequireAuth;
