import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Trash2 } from 'lucide-react';
import ComposePopup from '../components/ComposePopup';
import './styles/Drafts.css';

export default function Drafts() {
  const [drafts, setDrafts] = useState([]);
  const [selectedDraft, setSelectedDraft] = useState(null);
  const [showCompose, setShowCompose] = useState(false);
  const userId = '000';

  const fetchDrafts = () => {
    axios.get('http://localhost:8000/api/drafts', {
      params: { user_id: userId }
    })
    .then(res => setDrafts(res.data.items))
    .catch(err => console.error("Fetch error:", err));
  };

  const deleteDraft = (id) => {
    axios.delete(`http://localhost:8000/api/drafts/${userId}/${id}`)
      .then(fetchDrafts)
      .catch(err => console.error("Delete failed:", err));
  };

  const handleEdit = (draft) => {
    setSelectedDraft(draft);
    setShowCompose(true);
  };

  const handleCloseCompose = () => {
    setShowCompose(false);
    setSelectedDraft(null);
    fetchDrafts();
  };

  useEffect(() => {
    fetchDrafts();
  }, []);

  return (
    <div className="email-list">
      <h2 className="text-xl font-bold mb-4">Drafts</h2>
      {drafts.length === 0 ? (
        <p className="empty-message">No drafts saved.</p>
      ) : (
        drafts.map((draft) => (
          <div
            key={draft.draft_id}
            className="email-item"
            onClick={() => handleEdit(draft)}
          >
            <div className="email-content">
              <span className={`email-sender ${draft.from_ai ? 'ai-draft' : 'user-draft'}`}>
                {draft.from_ai ? 'AI-generated Draft' : 'Draft'}
              </span>
              <span className="email-subject">{draft.subject || '(No subject)'}</span>
              <span className="email-snippet">{draft.body?.slice(0, 100) || '(No content)'}</span>
            </div>
            <div className="email-meta">
              <button
                className="icon-button"
                title="Delete"
                onClick={(e) => {
                  e.stopPropagation();
                  deleteDraft(draft.draft_id);
                }}
              >
                <Trash2 size={16} />
              </button>
            </div>
          </div>
        ))
      )}

      {showCompose && (
        <ComposePopup
          draft={selectedDraft}
          onClose={handleCloseCompose}
        />
      )}
    </div>
  );
}