import React from 'react';
import { Link } from 'react-router-dom';
import { Inbox, Send, FileText, Star, Trash2, Pencil } from 'lucide-react';
import './Sidebar.css';

const Sidebar = ({ onCompose }) => {
  return (
    <div className="sidebar">
      <h2 className="sidebar-title">Lazy Mail</h2>

      <button className="compose-button" onClick={onCompose}>
        <Pencil size={18} />
        <span>Compose</span>
      </button>

      <ul className="sidebar-menu">
      <li>
        <Inbox size={18} />
        <Link to="/">Inbox</Link>
      </li>
      <li>
        <Send size={18} />
        <Link to="/sent">Sent</Link>
      </li>
      <li>
        <FileText size={18} />
        <Link to="/drafts">Drafts</Link>
      </li>
      <li>
          <Star size={18} />
          <span>Starred</span>
        </li>
        <li>
          <Trash2 size={18} />
          <span>Trash</span>
        </li>
      </ul>
    </div>
  );
};

export default Sidebar;
