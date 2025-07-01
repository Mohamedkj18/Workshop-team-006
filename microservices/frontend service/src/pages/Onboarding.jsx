import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './styles/Login.css';

export default function Onboarding() {
  const navigate = useNavigate();
  const [age, setAge] = useState('');
  const [occupation, setOccupation] = useState('');
  const [profileImage, setProfileImage] = useState(null);
  const [step, setStep] = useState(0);
  const [styleReady, setStyleReady] = useState(true);
  const [waitingForStyle, setWaitingForStyle] = useState(false);

  useEffect(() => {
    axios
      .post('http://localhost:8000/api/style/init', {
        user_id: '000', // Replace with actual user ID
      })
      .then(() => setStyleReady(true));
  }, []);

  const handleNext = (e) => {
    e.preventDefault();

    if (step < 2) {
      setStep(step + 1);
    } else {
      // Final step: wait for style to be ready
      if (styleReady) {
        console.log({ age, occupation, profileImage });
        navigate('/inbox');
      } else {
        setWaitingForStyle(true);
        const interval = setInterval(() => {
          if (styleReady) {
            clearInterval(interval);
            console.log({ age, occupation, profileImage });
            navigate('/inbox');
          }
        }, 1000);
      }
    }
  };

  const renderStep = () => {
    switch (step) {
      case 0:
        return (
          <input
            type="number"
            placeholder="Your Age"
            value={age}
            onChange={(e) => setAge(e.target.value)}
            required
          />
        );
      case 1:
        return (
          <input
            type="text"
            placeholder="Occupation / Role"
            value={occupation}
            onChange={(e) => setOccupation(e.target.value)}
            required
          />
        );
      case 2:
        return (
          <>
            <input
              type="file"
              accept=".png,.jpg,.jpeg"
              onChange={(e) => setProfileImage(e.target.files[0])}
              required
            />
            <p style={{ fontSize: '0.85rem', color: '#6b7280' }}>
              Upload a profile picture (PNG or JPG)
            </p>
          </>
        );
      default:
        return null;
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        {!waitingForStyle ? (
          <>
            <h1 className="login-title">Welcome to LazyMail 🎉</h1>
            <p className="login-subtitle">Let's get to know you better.</p>
            <form onSubmit={handleNext} className="login-form">
              {renderStep()}
              <button type="submit" className="login-button">
                {step < 2 ? 'Next' : 'Finish'}
              </button>
            </form>
          </>
        ) : (
          <>
            <h2 className="login-subtitle" style={{ marginBottom: '2rem' }}>
              Hang tight we’re finishing up your personalized setup
            </h2>
            <div className="spinner" />
          </>
        )}
      </div>
    </div>
  );
}
