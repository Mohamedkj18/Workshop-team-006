import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './styles/Login.css';

export default function Onboarding() {
  const navigate = useNavigate();
  const [age, setAge] = useState('');
  const [occupation, setOccupation] = useState('');
  const [profileImage, setProfileImage] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate backend init style learning
    axios.post('http://localhost:8000/api/style/init', {
      user_id: '000' // Replace with actual user ID/token-based logic
    }).finally(() => setLoading(false));
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    // TODO: Save onboarding details to backend
    console.log({ age, occupation, profileImage });
    navigate('/inbox');
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <h1 className="login-title">Welcome to LazyMail 🎉</h1>
        <p className="login-subtitle">Before we get started, tell us a bit more about yourself.</p>

        {loading && <p>Initializing your personalized style... ⏳</p>}

        <form onSubmit={handleSubmit} className="login-form">
          <input
            type="number"
            placeholder="Your Age"
            value={age}
            onChange={(e) => setAge(e.target.value)}
          />

          <input
            type="text"
            placeholder="Occupation / Role"
            value={occupation}
            onChange={(e) => setOccupation(e.target.value)}
          />

          <input
            type="file"
            accept="image/*"
            onChange={(e) => setProfileImage(e.target.files[0])}
          />

          <button type="submit" className="login-button">Finish Setup</button>
        </form>
      </div>
    </div>
  );
}
