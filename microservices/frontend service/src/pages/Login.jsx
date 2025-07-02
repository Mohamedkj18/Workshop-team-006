// src/pages/Login.jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FcGoogle } from 'react-icons/fc';
import './styles/Login.css';

export default function Login() {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleGoogleLogin = () => {
    window.location.href = import.meta.env.VITE_BACKEND_URL + "/auth/login";
  };

  const handleLogin = async (e) => {
    e.preventDefault();

    if (username && password) {
      // Simulated login
      localStorage.setItem('authToken', 'dummy');
      const userId = '000'; // For demo purposes

      navigate('/inbox');
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <h1 className="login-title">Welcome Back</h1>
        <p className="login-subtitle">Log in to your LazyMail account</p>

        <button onClick={handleGoogleLogin} className="google-signin-button">
          <FcGoogle style={{ fontSize: '1.5rem' }} />
          <span style={{ marginLeft: '0.5rem' }}>Sign in with Google</span>
        </button>

        <div className="divider">
          <span className="divider-text">or</span>
        </div>

        <form onSubmit={handleLogin} className="login-form">
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button type="submit" className="login-button">Login</button>
        </form>

        <div className="login-footer">
          <button
            className="link-button"
            onClick={() => alert('Password reset flow coming soon!')}
          >
            Forgot Password?
          </button>
          <p className="login-footer-text">
            New to LazyMail?{' '}
            <span onClick={() => navigate('/signup')} className="login-link">
              Create an account
            </span>
          </p>
        </div>
      </div>
    </div>
  );
}
