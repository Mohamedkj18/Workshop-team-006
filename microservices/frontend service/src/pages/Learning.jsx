// src/pages/Learning.jsx
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './styles/Learning.css';

export default function Learning() {
  const [stage, setStage] = useState(0);
  const navigate = useNavigate();

  const steps = [
    'Fetching your emails...',
    'Learning your writing style...',
    "Your style is: ✨ friendly & concise ✨"
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setStage(prev => {
        if (prev < steps.length - 1) return prev + 1;
        clearInterval(interval);
        setTimeout(() => navigate('/inbox'), 2000);
        return prev;
      });
    }, 2000);

    return () => clearInterval(interval);
  }, [navigate]);

  return (
    <div className="learning-container">
      <div className="learning-box">
        <h2 className="learning-title">Hang tight...</h2>
        <p className="learning-text">{steps[stage]}</p>
      </div>
    </div>
  );
}
