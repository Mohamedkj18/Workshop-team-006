// src/pages/Login.jsx
import React from 'react';
import { FcGoogle } from 'react-icons/fc';
import { useNavigate } from 'react-router-dom';
import './styles/Login.css'; // assumes the file is in src/styles/

export default function Login() {
  const navigate = useNavigate();

  const handleGoogleSignIn = () => {
    navigate('/learning');
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <h1 className="login-title">Lazy Email</h1>
        <p className="login-subtitle">Your AI-powered inbox assistant</p>
        <button onClick={handleGoogleSignIn} className="login-button">
          <FcGoogle className="google-icon" />
          Sign in with Gmail
        </button>
      </div>
    </div>
  );
}
