import React from 'react';
import './styles/Sent.css';

export default function Sent({ emails }) {
  return (
    <div className="sent-list">
      {emails.length === 0 ? (
        <p className="empty">No sent emails yet.</p>
      ) : (
        emails.map((email, index) => (
          <div key={index} className="sent-item">
            <div className="sent-subject">{email.subject}</div>
            <div className="sent-body">{email.body}</div>
          </div>
        ))
      )}
    </div>
  );
}
