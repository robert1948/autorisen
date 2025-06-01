import { useEffect, useState } from 'react';
import api from '../api/axios';

const Profile = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/me')
      .then((res) => {
        setUser(res.data);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Failed to load profile:', err);
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
        <p className="text-danger">Unable to load profile information.</p>
      </div>
    );
  }

  return (
    <div className="container mt-4">
      <div className="p-4 bg-white rounded shadow-sm">
        <h2 className="mb-3">My Profile</h2>
        <p className="lead">Here’s what we know about you:</p>

        <table className="table table-bordered mt-3">
          <tbody>
            <tr>
              <th scope="row">Full Name</th>
              <td>{user.full_name}</td>
            </tr>
            <tr>
              <th scope="row">Email</th>
              <td>{user.email}</td>
            </tr>
            <tr>
              <th scope="row">Role</th>
              <td>{user.role || 'N/A'}</td>
            </tr>
            <tr>
              <th scope="row">User ID</th>
              <td>{user.id || 'N/A'}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Profile;
