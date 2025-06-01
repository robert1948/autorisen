import { useEffect, useState } from 'react';
import api from '../api/axios';

const Dashboard = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/me')
      .then((res) => {
        setUser(res.data);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Failed to fetch user:', err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="container text-center mt-5">
        <div className="spinner-border text-primary" role="status" />
      </div>
    );
  }

  if (!user) {
    return (
      <div className="container text-center mt-5">
        <p className="text-danger">Unable to load user information.</p>
      </div>
    );
  }

  return (
    <div className="container mt-4">
      <div className="p-4 bg-white rounded shadow-sm">
        <h2 className="mb-3">Dashboard</h2>
        <p>Welcome, <strong>{user.full_name || user.email}</strong>.</p>
        <hr />
        <h5 className="mt-4">User Information</h5>
        <ul className="list-group">
          <li className="list-group-item"><strong>Email:</strong> {user.email}</li>
          <li className="list-group-item"><strong>Role:</strong> {user.role || 'N/A'}</li>
          <li className="list-group-item"><strong>User ID:</strong> {user.id || 'N/A'}</li>
        </ul>
      </div>
    </div>
  );
};

export default Dashboard;
