import React from 'react';
import './styles/GPTChat.css';

export default function GPTChat({ onClose }) {
  return (
    <div className="gpt-chat-popup">
      <div className="gpt-chat-header">
        Chat with GPT-4
        <button className="gpt-close-btn" onClick={onClose}>×</button>
      </div>
      <div className="gpt-chat-body">
        {/* GPT chat messages would appear here */}
      </div>
      <div className="gpt-chat-footer">
        <input type="text" className="gpt-chat-input" placeholder="Type a message..." />
        <button className="gpt-send-btn">Send</button>
      </div>
    </div>
  );
}
