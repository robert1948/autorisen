import React, { useEffect, useState } from 'react';
import axios from '../api/axios';
import { useNavigate } from 'react-router-dom';

function DeveloperOnboarding() {
  const [onboarding, setOnboarding] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const token = localStorage.getItem('token');
        const res = await axios.get('/developer/me', {
          headers: { Authorization: `Bearer ${token}` }
        });
        setOnboarding(res.data.onboarding || {});
      } catch (err) {
        setError('❌ Failed to load onboarding data.');
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, []); // 🚫 no token in deps – token doesn’t change across renders

  const handleToggle = async (step) => {
    const updated = { ...onboarding, [step]: !onboarding[step] };
    setMessage('');
    setError('');

    try {
      const token = localStorage.getItem('token');
      await axios.patch('/developer/onboarding', { onboarding: updated }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setOnboarding(updated);
      setMessage(`✅ Step "${step}" updated`);
    } catch (err) {
      setError('❌ Failed to update onboarding step.');
    }
  };

  const steps = [
    { key: 'upload_portfolio', label: 'Upload Portfolio' },
    { key: 'complete_profile', label: 'Complete Profile' },
    { key: 'connect_github', label: 'Connect GitHub' },
    { key: 'start_agent_task', label: 'Start First Agent Task' },
  ];

  return (
    <div className="container mt-5">
      <h2 className="mb-4">Developer Onboarding</h2>

      {loading && <p>Loading onboarding steps...</p>}

      {error && <div className="alert alert-danger">{error}</div>}
      {message && <div className="alert alert-success">{message}</div>}

      {!loading && !error && (
        <form className="list-group">
          {steps.map(({ key, label }) => (
            <label key={key} className="list-group-item d-flex align-items-center">
              <input
                type="checkbox"
                className="form-check-input me-2"
                checked={onboarding[key] || false}
                onChange={() => handleToggle(key)}
              />
              {label}
            </label>
          ))}
        </form>
      )}
    </div>
  );
}

export default DeveloperOnboarding;
