import React from 'react';
import './styles/EmailView.css';

export default function EmailView({ email, onBack }) {
  return (
    <div className="email-view">
      <button className="back-btn" onClick={onBack}>← Back</button>
      <h2>{email.subject}</h2>
      <h4>From: {email.sender}</h4>
      <p>{email.body || "Full message content goes here..."}</p>

      <div className="generated-reply">
        <h4>AI-Generated Reply</h4>
        <p>{email.generatedReply || "Thanks! I’ll get back to you soon."}</p>
      </div>
    </div>
  );
}
