import React, { useState } from 'react';
import { Star, StarOff, Trash2 } from 'lucide-react';
import './styles/EmailList.css';
import { ChevronDown, Square, RotateCcw, MoreVertical, ChevronLeft, ChevronRight } from 'lucide-react';


export default function EmailList({ onSelectEmail }) {
  const [emails, setEmails] = useState([
    {
      id: 1,
      sender: 'John Pork',
      subject: 'I am not dead',
      snippet: 'Hi team, just wanted to give a quick update on the project...',
      date: 'May 11',
    },
    {
      id: 2,
      sender: 'Amazon',
      subject: 'Your order has been shipped',
      snippet: 'Your package will arrive by tomorrow...',
      date: 'May 10',
    },
  ]);

  const [starred, setStarred] = useState(new Set());

  const toggleStar = (id) => {
    setStarred((prev) => {
      const updated = new Set(prev);
      updated.has(id) ? updated.delete(id) : updated.add(id);
      return updated;
    });
  };

  const deleteEmail = (id) => {
    setEmails((prev) => prev.filter((email) => email.id !== id));
  };

  return (
    <>
      {/* Scrollable white wrapper container should already exist in parent */}
      <div className="email-list-header">
        <div className="email-header-left">
          <div className="checkbox-dropdown">
            <Square size={16} />
            <ChevronDown size={16} />
          </div>
          <button className="icon-button" title="Refresh"><RotateCcw size={16} /></button>
          <button className="icon-button" title="More"><MoreVertical size={16} /></button>
        </div>
        <div className="email-header-right">
          <button className="icon-button" title="Older"><ChevronLeft size={16} /></button>
          <button className="icon-button" title="Newer"><ChevronRight size={16} /></button>
        </div>
      </div>



      {emails.map((email) => (
        <div key={email.id} className="email-item">
          <div className="email-selection">
            <input type="checkbox" className="email-checkbox" />
          </div>
          <div className="email-content" onClick={() => onSelectEmail(email)}>
            <span className="email-sender">{email.sender}</span>
            <span className="email-subject">{email.subject}</span>
            <span className="email-snippet">{email.snippet}</span>
            <span className="email-date">{email.date}</span>
            <button
              className="icon-button"
              onClick={(e) => {
                e.stopPropagation();
                toggleStar(email.id);
              }}
              title={starred.has(email.id) ? 'Unstar' : 'Star'}
            >
              {starred.has(email.id) ? (
                <Star size={16} color="#fbbc04" fill="#fbbc04" />
              ) : (
                <StarOff size={16} />
              )}
            </button>
            <button
              className="icon-button"
              onClick={(e) => {
                e.stopPropagation();
                deleteEmail(email.id);
              }}
              title="Delete"
            >
              <Trash2 size={16} />
            </button>
          </div>
        </div>

      ))}
    </>
  );
}
