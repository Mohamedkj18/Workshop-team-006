import React from 'react';
import { Trash2 } from 'lucide-react';
import './styles/Drafts.css';

export default function Drafts({ drafts, onEditDraft, onDeleteDraft }) {
  const handleClick = (draft) => {
    onEditDraft(draft);
  };

  return (
    <div className="email-list">
      {drafts.length === 0 ? (
        <p className="empty-message">No drafts saved.</p>
      ) : (
        drafts.map((draft) => (
          <div
            key={draft.id}
            className="email-item"
            onClick={() => handleClick(draft)}
          >
            <div className="email-content">
              <span className={`email-sender ${draft.type === 'ai' ? 'ai-draft' : 'user-draft'}`}>
                Draft
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
                  onDeleteDraft(draft.id);
                }}
              >
                <Trash2 size={16} />
              </button>
            </div>
          </div>
        ))
      )}
    </div>
  );
}
