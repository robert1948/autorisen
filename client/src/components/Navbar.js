import { Link, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { jwtDecode } from 'jwt-decode';
import axios from '../api/axios';

const Navbar = () => {
  const navigate = useNavigate();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [progress, setProgress] = useState(null);
  const { token, user, isAuthenticated, logout } = useAuth();

  const toggleDropdown = () => setDropdownOpen(!dropdownOpen);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  let displayName = 'User';
  if (token) {
    try {
      const decoded = jwtDecode(token);
      displayName = decoded.full_name || decoded.email || 'User';
    } catch {
      logout();
      navigate('/login');
    }
  }

  useEffect(() => {
    const fetchOnboarding = async () => {
      if (token && user?.sub) {
        try {
          const res = await axios.get('/developer/me', {
            headers: { Authorization: `Bearer ${token}` }
          });
          const onboarding = res.data?.onboarding || {};
          const steps = Object.values(onboarding);
          const completed = steps.filter(Boolean).length;
          setProgress({ completed, total: steps.length });
        } catch (err) {
          setProgress(null);
        }
      }
    };
    fetchOnboarding();
  }, [token, user]);

  const progressPercent = progress ? Math.round((progress.completed / progress.total) * 100) : 0;

  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-dark px-4">
      <Link className="navbar-brand" to="/">AutoAgent</Link>
      <ul className="navbar-nav ms-auto align-items-center">

        <li className="nav-item">
          <Link className="nav-link" to="/welcome">Welcome</Link>
        </li>

        {isAuthenticated ? (
          <>
            <li className="nav-item">
              <Link className="nav-link" to="/dashboard">Dashboard</Link>
            </li>

            {progress && (
              <li className="nav-item d-flex align-items-center px-2">
                <div className="text-light small text-nowrap me-2">
                  {progress.completed}/{progress.total}
                </div>
                <div className="progress" style={{ width: '80px', height: '6px' }}>
                  <div
                    className="progress-bar bg-success"
                    role="progressbar"
                    style={{ width: `${progressPercent}%` }}
                    aria-valuenow={progressPercent}
                    aria-valuemin="0"
                    aria-valuemax="100"
                  />
                </div>
              </li>
            )}

            <li className="nav-item dropdown">
              <button
                className="btn btn-link nav-link dropdown-toggle"
                onClick={toggleDropdown}
              >
                Hello, {displayName}
              </button>
              {dropdownOpen && (
                <ul className="dropdown-menu dropdown-menu-end show">
                  <li><Link className="dropdown-item" to="/profile">Profile</Link></li>
                  <li><Link className="dropdown-item" to="/onboarding">Onboarding</Link></li>
                  <li><button className="dropdown-item" onClick={handleLogout}>Logout</button></li>
                </ul>
              )}
            </li>
          </>
        ) : (
          <>
            <li className="nav-item">
              <Link className="nav-link" to="/login">Login</Link>
            </li>
            <li className="nav-item">
              <Link className="nav-link" to="/register-user">Register</Link>
            </li>
          </>
        )}
      </ul>
    </nav>
  );
};

export default Navbar;
