// client/src/components/Welcome.js

import React from 'react';
import { Link } from 'react-router-dom';

function Welcome() {
  return (
    <div className="container mt-4 text-center">
      <h1>Welcome to AutoAgent!</h1>
      <p>
        AutoAgent is your intelligent agent platform powered by FastAPI, React, and AI.
        It’s designed to help you build smart agents and automate your workflows seamlessly.
      </p>
      <p>
        Register as a user or developer to get started. Explore our developer onboarding process,
        your personalized dashboard, and your profile.
      </p>
      <hr />
      <h2>Why Choose AutoAgent?</h2>
      <ul className="list-unstyled">
        <li>✅ Create smart agents with easy onboarding</li>
        <li>✅ View your tasks and workflow in the dashboard</li>
        <li>✅ Enjoy a clean and responsive user interface</li>
      </ul>
      <p>
        We’re continuously improving AutoAgent to boost your productivity and add exciting new features.
        Feel free to share any suggestions!
      </p>

      {/* Action Buttons for User Response */}
      <div className="mt-4">
        <Link to="/register-user" className="btn btn-primary mx-2">
          Register as User
        </Link>
        <Link to="/register-developer" className="btn btn-success mx-2">
          Register as Developer
        </Link>
        <Link to="/login" className="btn btn-outline-secondary mx-2">
          Log In
        </Link>
      </div>
    </div>
  );
}

export default Welcome;
