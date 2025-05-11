import React, { useState, useRef, useEffect } from 'react';
import './ComposePopup.css';
import {
  Paperclip,
  Image,
  Wand2,
  Trash2,
  Signature,
  Calendar,
  Link2
} from 'lucide-react';

export default function ComposePopup({ onClose, onSend }) {
  const [to, setTo] = useState('');
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [isMinimized, setIsMinimized] = useState(false);
  const [isFullSize, setIsFullSize] = useState(false);
  const [showSendOptions, setShowSendOptions] = useState(false);

  const sendContainerRef = useRef();

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        sendContainerRef.current &&
        !sendContainerRef.current.contains(event.target)
      ) {
        setShowSendOptions(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSend = (option) => {
    console.log(`${option}:`, { to, subject, body });
    if (option === 'Send') onSend({ to, subject, body });
    onClose();
  };

  const toggleMinimize = () => setIsMinimized((prev) => !prev);
  const toggleResize = () => setIsFullSize((prev) => !prev);

  if (isMinimized) {
    return (
      <div className="compose-popup minimized" onClick={toggleMinimize}>
        <span className="minimized-subject">{subject || 'New Message'}</span>
      </div>
    );
  }
  

  return (
    <div className={`compose-popup ${isFullSize ? 'fullsize' : ''}`}>
      <div className="compose-topbar">
        <div className="compose-title">{subject || 'New Message'}</div>
        <div className="topbar-controls">
          <button title="Minimize" onClick={toggleMinimize}>−</button>
          <button title="Resize" onClick={toggleResize}>⛶</button>
          <button title="Close" onClick={onClose}>×</button>
        </div>
      </div>

      <input
        type="text"
        placeholder="To"
        value={to}
        onChange={(e) => setTo(e.target.value)}
      />
      <input
        type="text"
        placeholder="Subject"
        value={subject}
        onChange={(e) => setSubject(e.target.value)}
      />
      <textarea
        placeholder="Write your message..."
        value={body}
        onChange={(e) => setBody(e.target.value)}
      />

      <div className="compose-footer">
        <div className="send-group" ref={sendContainerRef}>
          <div className="send-button-wrapper">
            <button className="send-main" onClick={() => handleSend('Send')}>
              Send
            </button>
            <button
              className="send-toggle"
              onClick={(e) => {
                e.stopPropagation();
                setShowSendOptions((prev) => !prev);
              }}
            >
              ⌄
            </button>

            {showSendOptions && (
              <div className="send-dropdown-menu">
                <div onClick={() => handleSend('Send')}>Send</div>
                <div onClick={() => handleSend('Schedule')}>Schedule</div>
                <div onClick={() => handleSend('Save Draft')}>Save Draft</div>
              </div>
            )}
          </div>
        </div>

        <div className="icon-bar">
          <button className="icon-button" title="Attach file"><Paperclip size={18} /></button>
          <button className="icon-button" title="Insert photo"><Image size={18} /></button>
          <button className="icon-button" title="Insert signature"><Signature size={18} /></button>
          <button className="icon-button" title="Schedule meeting"><Calendar size={18} /></button>
          <button className="icon-button" title="Insert link"><Link2 size={18} /></button>
          <button className="icon-button" title="Discard draft" onClick={onClose}><Trash2 size={18} /></button>

          <button className="smart-reply-btn" title="Let AI help you write">
            <Wand2 size={16} style={{ marginRight: '4px' }} />
            Smart Reply ✨
          </button>
        </div>
      </div>
    </div>
  );
}
