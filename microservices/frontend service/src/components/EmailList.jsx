import React from 'react';
import { Star, StarOff, Trash2, RotateCcw, MoreVertical, ChevronLeft, ChevronRight, Square, ChevronDown, CornerUpLeft } from 'lucide-react';
import './styles/EmailList.css';

/**
 * Centralized config for per-type actions.
 * Each type maps to an array of action keys, which are rendered if the corresponding handler is passed.
 */
const typeActions = {
  inbox:    ['star', 'trash'],
  sent:     ['trash'],
  drafts:   ['trash', 'delete'],
  starred:  ['star', 'trash'],
  trash:    ['restore', 'delete'],
};

export default function EmailList({
  emails = [],
  onSelectEmail,
  onStar,
  onTrash,
  onDelete,
  onRestore,
  starred = new Set(),
  trashed = new Set(),
  type,
}) {
  const actions = typeActions[type] || [];

  // Centralized action renderers: only render if handler is passed
  const actionRenderers = {
    star: (email) =>
      onStar && (
        <button
          className="icon-button"
          onClick={e => {
            e.stopPropagation();
            onStar(email.id);
          }}
          title={starred.has(email.id) ? 'Unstar' : 'Star'}
        >
          {starred.has(email.id) ? (
            <Star size={16} color="#fbbc04" fill="#fbbc04" />
          ) : (
            <StarOff size={16} />
          )}
        </button>
      ),
    trash: (email) =>
      onTrash && (
        <button
          className="icon-button"
          onClick={e => {
            e.stopPropagation();
            onTrash(email.id);
          }}
          title="Move to Trash"
        >
          <Trash2 size={16} />
        </button>
      ),
    delete: (email) =>
      onDelete && (
        <button
          className="icon-button"
          onClick={e => {
            e.stopPropagation();
            onDelete(email.id);
          }}
          title={type === 'drafts' ? "Delete Draft" : "Delete Forever"}
        >
          <Trash2 size={16} />
        </button>
      ),
    restore: (email) =>
      onRestore && (
        <button
          className="icon-button"
          onClick={e => {
            e.stopPropagation();
            onRestore(email.id);
          }}
          title="Restore"
        >
          <CornerUpLeft size={16} />
        </button>
      ),
  };

  return (
    <div className="email-inner">
      <div className="email-list-header">
        <div className="email-header-left">
          <div className="checkbox-dropdown">
            <Square size={16} />
            <ChevronDown size={16} />
            {/* <ChevronDown size={16} /> */}
          </div>
          <button className="icon-button" title="Refresh"><RotateCcw size={16} /></button>
          <button className="icon-button" title="More"><MoreVertical size={16} /></button>
        </div>
        <div className="email-header-right">
          <button className="icon-button" title="Older"><ChevronLeft size={16} /></button>
          <button className="icon-button" title="Newer"><ChevronRight size={16} /></button>
        </div>
      </div>

      {emails.length === 0 && (
        <div className="empty-list">No emails to display.</div>
      )}

      {emails.map((email) => (
        <div key={email.id} className="email-item">
          <div className="email-selection">
            <input type="checkbox" className="email-checkbox" />
          </div>
          <div
            className="email-content"
            onClick={() => onSelectEmail(email)}
            style={{ cursor: 'pointer' }}
          >
            <span className="email-sender">{email.sender}</span>
            <span className="list-subject">{email.subject}</span>
            <span className="email-snippet">{email.snippet || (email.body ? email.body.slice(0, 40) + '...' : '')}</span>
            <span className="email-date">{email.date}</span>
            {/* Render actions for this type, only if handler is passed */}
            {actions.map(action =>
              actionRenderers[action] ? (
                <React.Fragment key={action}>
                  {actionRenderers[action](email)}
                </React.Fragment>
              ) : null
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
