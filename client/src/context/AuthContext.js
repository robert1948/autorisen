import { createContext, useContext, useState, useEffect } from 'react';
import { jwtDecode } from 'jwt-decode';
import axios from '../api/axios'; // Adjusted path!

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(() => localStorage.getItem('token'));
  const [user, setUser] = useState(null); // decoded JWT
  const [userProfile, setUserProfile] = useState(null); // fetched profile
  const [onboarding, setOnboarding] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProfile = async () => {
      if (!token) {
        setUser(null);
        setUserProfile(null);
        setLoading(false);
        return;
      }

      try {
        const decoded = jwtDecode(token);
        const now = Date.now() / 1000;
        if (decoded.exp < now) throw new Error('Token expired');

        setUser(decoded);

        const res = await axios.get('/developer/me', {
          headers: { Authorization: `Bearer ${token}` },
        });

        setUserProfile(res.data);
        setOnboarding(res.data.onboarding || {});
      } catch (err) {
        logout(); // Invalid or expired token
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, [token]);

  const login = (newToken) => {
    localStorage.setItem('token', newToken);
    setToken(newToken);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    setUserProfile(null);
    setOnboarding({});
  };

  return (
    <AuthContext.Provider
      value={{
        token,
        user,
        userProfile,
        onboarding,
        setOnboarding,
        isAuthenticated: !!user,
        login,
        logout,
        loading
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
