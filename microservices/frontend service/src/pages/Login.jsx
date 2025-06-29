// src/pages/Login.jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FcGoogle } from 'react-icons/fc';
import './styles/Login.css';
import { useEffect, useRef } from 'react';

export default function Login() {
  const googleBtn = useRef();
  const navigate = useNavigate();

  useEffect(() => {
    window.google.accounts.id.initialize({
      client_id: 'YOUR_GOOGLE_CLIENT_ID',
      callback: handleCredentialResponse
    });

    window.google.accounts.id.renderButton(googleBtn.current, {
      theme: 'outline',
      size: 'large',
      width: 280,
    });
  }, []);

  const handleCredentialResponse = (response) => {
    console.log('Google JWT:', response.credential);
    // TODO: send token to backend for validation
    localStorage.setItem('authToken', response.credential);
    navigate('/inbox');
  };

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = (e) => {
    e.preventDefault();
    // TODO: Add real authentication logic
    if (username && password) {
      localStorage.setItem('authToken', 'dummy');
      navigate('/inbox');
    }
  };

  const handleGoogleLogin = () => {
    // TODO: Implement Google OAuth
    alert("Google Sign-In coming soon");
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <div ref={googleBtn} className="google-signin-button" />
        <h1 className="login-title">Welcome Back</h1>
        <p className="login-subtitle">Log in to your LazyMail account</p>

        <button onClick={handleGoogleLogin} className="login-button">
          <FcGoogle className="google-icon" />
          Sign in with Gmail
        </button>

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
          <button className="link-button" onClick={() => alert('Password reset flow coming soon!')}>Forgot Password?</button>
          <p className="login-footer-text">
            New to LazyMail? <span onClick={() => navigate('/signup')} className="login-link">Create an account</span>
          </p>
        </div>
      </div>
    </div>
  );
}
