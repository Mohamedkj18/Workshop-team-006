import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './styles/Login.css';

export default function Signup() {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [email, setEmail] = useState('');

  const handleSignup = (e) => {
    e.preventDefault();
    // TODO: POST to signup endpoint
    if (username && password && email) {
      localStorage.setItem('authToken', 'dummy'); // Replace with real token
      navigate('/onboarding');
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <h1 className="login-title">Create Your LazyMail Account</h1>
        <p className="login-subtitle">Get started with your AI-powered inbox</p>

        <form onSubmit={handleSignup} className="login-form">
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
          <input
            type="email"
            placeholder="Gmail Address"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button type="submit" className="login-button">Continue</button>
        </form>

        <p className="login-footer-text">
          Already have an account? <span onClick={() => navigate('/login')} className="login-link">Log in</span>
        </p>
      </div>
    </div>
  );
}
