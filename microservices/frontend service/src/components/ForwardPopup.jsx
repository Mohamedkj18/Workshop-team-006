import React, { useState } from 'react';
import {
  Send, Trash2, Sparkles, Paperclip, Smile, Image, Link, Calendar
} from 'lucide-react';
import './styles/ForwardPopup.css';

export default function ForwardPopup({ originalEmail, onClose, onSend }) {
  const [to, setTo] = useState('');
  const [message, setMessage] = useState('');

  const handleSend = () => {
    onSend?.({ to, message });
    onClose?.();
  };

  return (
    <div className="forward-popup">
      <div className="forward-header">
        <input
          type="text"
          placeholder="To"
          value={to}
          onChange={(e) => setTo(e.target.value)}
          className="forward-input"
        />
      </div>

      <div className="forward-body">
        <textarea
          className="forward-textarea"
          placeholder="Write your message..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
        />

        {/* Forwarded original content */}
        <div className="forward-original">
          <p>---------- Forwarded message ----------</p>
          <p><strong>From:</strong> {originalEmail.sender} &lt;{originalEmail.senderEmail || 'unknown@email.com'}&gt;</p>
          <p><strong>Date:</strong> {originalEmail.date}</p>
          <p><strong>Subject:</strong> {originalEmail.subject}</p>
          <p><strong>To:</strong> me</p>
          <div style={{ whiteSpace: 'pre-wrap', marginTop: '0.5rem' }}>{originalEmail.body}</div>
        </div>
      </div>

      <div className="forward-toolbar">
        <div className="send-section">
          <button className="send-btn" onClick={handleSend}>
            Send <Send size={14} />
          </button>
        </div>

        <div className="icon-section">
          <button><Paperclip size={16} /></button>
          <button><Image size={16} /></button>
          <button><Link size={16} /></button>
          <button><Calendar size={16} /></button>
          <button><Smile size={16} /></button>
        </div>

        <button className="smart-email-btn">
          <Sparkles size={16} /> Smart Email
        </button>

        <button className="trash-btn" onClick={onClose}>
          <Trash2 size={16} />
        </button>
      </div>
    </div>
  );
}
