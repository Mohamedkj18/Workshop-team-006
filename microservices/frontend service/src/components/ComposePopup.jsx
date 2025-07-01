import React, { useState, useRef, useEffect } from 'react';
import './styles/ComposePopup.css';
import {
  Paperclip,
  Image,
  Wand2,
  Trash2,
  Signature,
  Calendar,
  Link2
} from 'lucide-react';
import axios from 'axios';

export default function ComposePopup({ onClose, draft }) {
  const [to, setTo] = useState('');
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [isMinimized, setIsMinimized] = useState(false);
  const [isFullSize, setIsFullSize] = useState(false);
  const [showSendOptions, setShowSendOptions] = useState(false);
  const [sendAction, setSendAction] = useState('Send');

  const [showAiChat, setShowAiChat] = useState(false);
  const [aiPrompt, setAiPrompt] = useState('');
  const [aiResponse, setAiResponse] = useState('');
  const [loadingResponse, setLoadingResponse] = useState(false);
  const userId = '000';
  const sendContainerRef = useRef();
  const isEditing = !!draft;

  useEffect(() => {
    if (draft) {
      setTo(draft.to?.[0] || '');
      setSubject(draft.subject || '');
      setBody(draft.body || '');
    }
  }, [draft]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (sendContainerRef.current && !sendContainerRef.current.contains(event.target)) {
        setShowSendOptions(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSend = async () => {
    const payload = {
      subject,
      body,
      to: [to]
    };

    try {
      if (sendAction === 'Save Draft') {
        if (isEditing) {
          await axios.put(`http://localhost:8000/api/drafts/${draft.draft_id}`, payload, {params: { user_id: userId }});
        } else {
          await axios.post(`http://localhost:8000/api/drafts`, {
            ...payload,
            thread_id: draft?.thread_id || crypto.randomUUID(),
            from_ai: draft?.from_ai ?? false,
          }, {params: { user_id: userId }});
        }
        alert('Draft saved.');
      } else if (sendAction === 'Send') {
        await axios.put(`http://localhost:8000/api/drafts/mark-draft-as-sent/${draft.draft_id}`, payload, {params: { user_id: userId }});
        alert('Draft marked as sent.');
      } else if (sendAction === 'Schedule') {
        console.log('Schedule feature coming soon...');
      }
      onClose();
    } catch (err) {
      console.error('Send/save failed:', err);
    }

    setShowSendOptions(false);
  };

  const handleApprove = async () => {
    try {
      await axios.put(`http://localhost:8000/api/drafts/mark-draft-as-approved/${draft.draft_id}`, payload, {params: { user_id: userId }});
      alert('Draft approved!');
      onClose();
    } catch (err) {
      console.error('Approve failed:', err);
    }
  };

  const handleDelete = async () => {
    try {
      await axios.delete(`http://localhost:8000/api/drafts/${draft.draft_id}`, {params: { user_id: userId }});
      alert('Draft deleted.');
      onClose();
    } catch (err) {
      console.error('Delete failed:', err);
    }
  };

  const handleOptionSelect = (option) => {
    setSendAction(option);
    setShowSendOptions(false);
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
        <div className="compose-title">
          {subject || 'New Message'}
          {draft?.from_ai && <span className="compose-badge ai">AI Draft</span>}
          {!draft?.from_ai && isEditing && <span className="compose-badge user">User Draft</span>}
        </div>
        <div className="topbar-controls">
          <button title="Minimize" onClick={toggleMinimize}>−</button>
          <button title="Resize" onClick={toggleResize}>⛶</button>
          <button title="Close" onClick={onClose}>×</button>
        </div>
      </div>

      <input type="text" placeholder="To" value={to} onChange={(e) => setTo(e.target.value)} />
      <input type="text" placeholder="Subject" value={subject} onChange={(e) => setSubject(e.target.value)} />
      <textarea placeholder="Write your message..." value={body} onChange={(e) => setBody(e.target.value)} />

      <div className="compose-footer">
        <div className="send-group" ref={sendContainerRef}>
          <div className="send-button-wrapper">
            <button className="send-main" onClick={handleSend}>
              {sendAction}
            </button>
            <button className="send-toggle" onClick={() => setShowSendOptions((prev) => !prev)}>⌄</button>

            {showSendOptions && (
              <div className="send-dropdown-menu">
                {['Send', 'Schedule', 'Save Draft'].map((option) => (
                  <div key={option} onClick={() => handleOptionSelect(option)}>
                    {option}
                  </div>
                ))}
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
          {isEditing && (
            <button className="icon-button" title="Delete Draft" onClick={handleDelete}>
              <Trash2 size={18} />
            </button>
          )}
          <button className="smart-reply-btn" title="Let AI help you write" onClick={() => setShowAiChat(true)}>
            <Wand2 size={16} />
            Smart Email ✨
          </button>
        </div>

        {showAiChat && (
          <div className="ai-chat-popup">
            <div className="ai-chat-header">
              Chat with GPT-4
              <button onClick={() => setShowAiChat(false)}>×</button>
            </div>
            <textarea
              className="ai-chat-input"
              placeholder="Ask AI to draft something for you..."
              value={aiPrompt}
              onChange={(e) => setAiPrompt(e.target.value)}
            />
            <button
              className="ai-chat-submit"
              disabled={loadingResponse}
              onClick={async () => {
                setLoadingResponse(true);
                try {
                  const res = await fetch("http://localhost:8000/api/ai/generate-email", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ user_id: userId, prompt: aiPrompt }),
                  });
                  const data = await res.json();
                  const reply = data.body || "No reply received.";
                  setBody(prev => prev + "\\n\\n" + reply);
                  setAiResponse('Response inserted into email');
                } catch (err) {
                  setAiResponse("Failed to get response from AI.");
                } finally {
                  setLoadingResponse(false);
                }
              }}
            >
              {loadingResponse ? "Generating..." : "Ask AI"}
            </button>
            {aiResponse && <p className="ai-chat-result">{aiResponse}</p>}
          </div>
        )}
      </div>
    </div>
  );
}