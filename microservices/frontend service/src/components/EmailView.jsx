import React, { useState } from 'react';
import {
  ArrowLeft,
  ChevronLeft,
  ChevronRight,
  Archive,
  Trash2,
  AlertTriangle,
  Mail,
  Star,
  Reply,
  User
} from 'lucide-react';

import ReplyPopup from './ReplyPopup';
import ForwardPopup from './ForwardPopup';
import './styles/EmailView.css';

// Centralized config for per-type logic
const mailboxTypeConfig = {
  inbox: {
    show: {
      archive: true,
      spam: true,
      delete: true,
      markUnread: true,
      star: true,
      reply: true,
      forward: true,
      restore: false,
      deleteForever: false,
      edit: false,
      toField: false,
      fromField: true,
    }
  },
  starred: {
    show: {
      archive: true,
      spam: true,
      delete: true,
      markUnread: true,
      star: true,
      reply: true,
      forward: true,
      restore: false,
      deleteForever: false,
      edit: false,
      toField: false,
      fromField: true,
    }
  },
  sent: {
    show: {
      archive: false,
      spam: false,
      delete: true,
      markUnread: false,
      star: false,
      reply: false,
      forward: false,
      restore: false,
      deleteForever: false,
      edit: false,
      toField: true,
      fromField: false,
    }
  },
  trash: {
    show: {
      archive: false,
      spam: false,
      delete: false,
      markUnread: false,
      star: false,
      reply: false,
      forward: false,
      restore: true,
      deleteForever: true,
      edit: false,
      toField: false,
      fromField: true,
    }
  },
  drafts: {
    show: {
      archive: false,
      spam: false,
      delete: true,
      markUnread: false,
      star: false,
      reply: false,
      forward: false,
      restore: false,
      deleteForever: false,
      edit: true,
      toField: true,
      fromField: false,
    }
  }
};

export default function EmailView({
  email,
  onBack,
  type = 'inbox',
  onArchive,
  onSpam,
  onDelete,
  onMarkUnread,
  onStar,
  onUnstar,
  onReply,
  onForward,
  onRestore,
  onDeleteForever,
  onEditDraft
}) {
  const [showReply, setShowReply] = useState(false);
  const [showForward, setShowForward] = useState(false);

  const config = mailboxTypeConfig[type] || mailboxTypeConfig['inbox'];
  const show = config.show;

  // Handler wrappers for popups
  const handleReply = () => {
    setShowReply(true);
    if (onReply) onReply(email);
  };
  const handleForward = () => {
    setShowForward(true);
    if (onForward) onForward(email);
  };

  return (
    <div className="email-view-wrapper">
      <div className="email-inner">
        {/* Top Action Bar */}
        <div className="email-top-bar">
          <div className="email-header-left">
            <button className="icon-button" onClick={onBack}><ArrowLeft size={16} /></button>
            {show.archive && onArchive && (
              <button className="icon-button" title="Archive" onClick={() => onArchive(email)}><Archive size={16} /></button>
            )}
            {show.spam && onSpam && (
              <button className="icon-button" title="Report spam" onClick={() => onSpam(email)}><AlertTriangle size={16} /></button>
            )}
            {show.delete && onDelete && (
              <button className="icon-button" title="Delete" onClick={() => onDelete(email)}><Trash2 size={16} /></button>
            )}
            {show.markUnread && onMarkUnread && (
              <button className="icon-button" title="Mark as unread" onClick={() => onMarkUnread(email)}><Mail size={16} /></button>
            )}
            {show.restore && onRestore && (
              <button className="icon-button" title="Restore" onClick={() => onRestore(email)}>Restore</button>
            )}
            {show.deleteForever && onDeleteForever && (
              <button className="icon-button" title="Delete Forever" onClick={() => onDeleteForever(email)}>Delete Forever</button>
            )}
          </div>
          <div className="email-header-right">
            <button className="icon-button" title="Older"><ChevronLeft size={16} /></button>
            <button className="icon-button" title="Newer"><ChevronRight size={16} /></button>
          </div>
        </div>

        <h2 className="view-subject">{email.subject}</h2>

        {/* Sender/Recipient Info */}
        <div className="email-header">
          <div className="sender-info">
            <div className="sender-avatar">
              {email.profileImage ? (
                <img src={email.profileImage} alt="Sender" />
              ) : (
                <div className="default-avatar"><User size={20} /></div>
              )}
            </div>
            <div className="sender-meta">
              {show.fromField && (
                <>
                  <div className="sender-name">{email.sender}</div>
                  <div className="sender-email">{email.senderEmail || 'unknown@email.com'}</div>
                </>
              )}
              {show.toField && (
                <>
                  <div className="sender-name">{email.recipient || email.to || 'Recipient'}</div>
                  <div className="sender-email">{email.recipientEmail || email.toEmail || 'unknown@email.com'}</div>
                </>
              )}
            </div>
          </div>

          <div className="header-actions">
            <span className="email-date">{email.date}</span>
            {show.star && (onStar || onUnstar) && (
              <button
                className="icon-button"
                title={email.starred ? "Unstar" : "Star"}
                onClick={() => (email.starred ? onUnstar(email) : onStar(email))}
              >
                <Star size={18} fill={email.starred ? "#FFD700" : "none"} />
              </button>
            )}
            {show.reply && (
              <button className="icon-button" title="Reply" onClick={handleReply}><Reply size={18} /></button>
            )}
          </div>
        </div>

        {/* Email Body */}
        <div className="email-body">
          <p>{email.body || "Full message content goes here..."}</p>
        </div>

        {/* Reply/Forward/Edit Buttons */}
        <div className="email-actions">
          {show.reply && (
            <button className="action-button" onClick={handleReply}>Reply</button>
          )}
          {show.forward && (
            <button className="action-button" onClick={handleForward}>Forward</button>
          )}
          {show.edit && onEditDraft && (
            <button className="action-button" onClick={() => onEditDraft(email)}>Edit Draft</button>
          )}
        </div>

        {/* Popups */}
        {show.reply && showReply && (
          <ReplyPopup
            recipient={{ name: email.sender, email: email.senderEmail || 'unknown@email.com' }}
            onClose={() => setShowReply(false)}
            onSend={(msg) => {
              if (onReply) onReply(msg);
              setShowReply(false);
            }}
          />
        )}

        {show.forward && showForward && (
          <ForwardPopup
            originalEmail={email}
            onClose={() => setShowForward(false)}
            onSend={({ to, message }) => {
              if (onForward) onForward({ to, message });
              setShowForward(false);
            }}
          />
        )}
      </div>
    </div>
  );
}
