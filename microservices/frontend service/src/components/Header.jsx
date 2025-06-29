import React from 'react';
import { Link } from 'react-router-dom';
import './styles/Header.css';

export default function Header() {
  return (
    <header className="main-header">
      <div className="header-content">
        <div className="logo-container">
          <img src="/Logo.png" alt="LazyMail Logo" className="logo" />
          <span className="brand-name">LazyMail</span>
        </div>
        <div className="auth-links">
          <Link to="/signup" className="btn">Sign Up</Link>
          <Link to="/login" className="btn secondary">Login</Link>
        </div>
      </div>
    </header>
  );
}
