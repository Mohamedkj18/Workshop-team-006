import React, { useState } from 'react';
import {
  Send, Trash2, Sparkles, Paperclip, Smile, Image, Link, Calendar
} from 'lucide-react';
import './styles/ReplyPopup.css';
import axios from 'axios';

export default function ReplyPopup({ recipient, emailId, userId, originalBody, onClose }) {
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [aiError, setAiError] = useState('');

  const handleSend = async () => {
    try {
      const token = localStorage.getItem('authToken');
      await axios.post(
        `http://localhost:8000/api/emails/${emailId}/reply`,
        { reply_body: message,
        reply_to_all:false,
        additional_cc: '',
        additional_bcc: '' },
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );
      onClose?.();
    } catch (err) {
      console.error('Failed to send reply:', err);
    }
  };

  const handleSmartReply = async () => {
    setLoading(true);
    setAiError('');
    try {
      const res = await axios.post('http://localhost:8000/api/ai/generate-reply', {
        user_id: userId,
        email_body: originalBody
      });
      const aiReply = res.data?.body || '';
      setMessage(prev => prev + '\n\n' + aiReply);
    } catch (err) {
      console.error('AI smart reply failed:', err);
      setAiError('Smart reply failed. Try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="reply-popup">
      <div className="reply-header">
        <span className="reply-to">↩ {recipient.name} &lt;{recipient.email}&gt;</span>
      </div>

      <div className="reply-body">
        <textarea
          className="reply-textarea"
          placeholder="Write your reply..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
        />
      </div>

      <div className="reply-toolbar">
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

        <button className="smart-email-btn" onClick={handleSmartReply} disabled={loading}>
          <Sparkles size={16} /> {loading ? 'Generating...' : 'Smart Reply'}
        </button>

        <button className="trash-btn" onClick={onClose}>
          <Trash2 size={16} />
        </button>
      </div>

      {aiError && <div className="ai-error">{aiError}</div>}
    </div>
  );
}
