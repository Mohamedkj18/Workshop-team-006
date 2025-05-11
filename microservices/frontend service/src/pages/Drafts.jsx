import React from 'react';
import { Pencil, Trash2 } from 'lucide-react';
import './styles/Drafts.css';

export default function Drafts({ drafts, onEditDraft, onDeleteDraft }) {
  return (
    <div className="drafts-list">
      {drafts.length === 0 ? (
        <p className="empty">No drafts saved.</p>
      ) : (
        drafts.map((draft) => (
          <div key={draft.id} className="draft-item">
            <div className="draft-info" onClick={() => onEditDraft(draft)}>
              <span className="draft-subject">{draft.subject || "(No subject)"}</span>
              <span className="draft-snippet">{draft.body?.slice(0, 80) || "No content..."}</span>
            </div>
            <div className="draft-actions">
              <Pencil size={16} className="icon-button" onClick={() => onEditDraft(draft)} title="Edit" />
              <Trash2 size={16} className="icon-button" onClick={() => onDeleteDraft(draft.id)} title="Delete" />
            </div>
          </div>
        ))
      )}
    </div>
  );
}
