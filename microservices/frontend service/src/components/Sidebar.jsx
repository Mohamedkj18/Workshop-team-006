import React from 'react';
import { Link } from 'react-router-dom';
import { Inbox, Send, FileText, Star, Trash2, Pencil } from 'lucide-react';
import './styles/Sidebar.css';

export default function Sidebar({ onCompose }) {
  return (
    <div className="sidebar">
      <button className="compose-button" onClick={onCompose}>
        <Pencil size={18} />
        <span>Compose</span>
      </button>

      <ul className="sidebar-menu">
        <li><Inbox size={18} /><Link to="/inbox">Inbox</Link></li>
        <li><Send size={18} /><Link to="/sent">Sent</Link></li>
        <li><FileText size={18} /><Link to="/drafts">Drafts</Link></li>
        <li><Star size={18} /><Link to="/starred">Starred</Link></li>
        <li><Trash2 size={18} /><Link to="/trash">Trash</Link></li>
      </ul>
    </div>
  );
}
