import React, { useState } from 'react';
import { Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import TopBar from './components/TopBar';
import EmailList from './components/EmailList';
import Drafts from './pages/Drafts';
import Sent from './pages/Sent';
import ComposePopup from './components/ComposePopup';
import './App.css';

export default function App() {
  const [showCompose, setShowCompose] = useState(false);
  const [editingDraft, setEditingDraft] = useState(null);
  const [drafts, setDrafts] = useState([]);
  const [sentEmails, setSentEmails] = useState([]);

  const handleCompose = () => {
    setEditingDraft(null);
    setShowCompose(true);
  };

  const handleSend = (email) => {
    setSentEmails(prev => [...prev, email]);
    setShowCompose(false);
    setEditingDraft(null);
  };

  const handleSaveDraft = (draft) => {
    const updated = {
      ...draft,
      id: draft.id || Date.now()
    };
    setDrafts(prev => {
      const existing = prev.find(d => d.id === updated.id);
      return existing
        ? prev.map(d => (d.id === updated.id ? updated : d))
        : [...prev, updated];
    });
    setShowCompose(false);
    setEditingDraft(null);
  };

  const handleEditDraft = (draft) => {
    setEditingDraft(draft);
    setShowCompose(true);
  };

  const handleDeleteDraft = (id) => {
    setDrafts(prev => prev.filter(d => d.id !== id));
  };

  return (
    <div className="app-container">
      <Sidebar onCompose={handleCompose} />
      <div className="main-panel">
        <TopBar />
        <div className="content-area">
          <Routes>
            <Route path="/" element={<EmailList />} />
            <Route path="/sent" element={<Sent emails={sentEmails} />} />
            <Route path="/drafts" element={
              <Drafts
                drafts={drafts}
                onEditDraft={handleEditDraft}
                onDeleteDraft={handleDeleteDraft}
              />
            } />
          </Routes>
        </div>
      </div>

      {showCompose && (
        <ComposePopup
          onClose={() => {
            setShowCompose(false);
            setEditingDraft(null);
          }}
          onSend={handleSend}
          onSaveDraft={handleSaveDraft}
          draft={editingDraft}
        />
      )}
    </div>
  );
}
