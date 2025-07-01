import React, { useState } from 'react';
import { Search, User, Settings, Sparkles } from 'lucide-react';
import GPTChat from './GPTChat';
import './styles/TopBar.css';

const TopBar = () => {
  const [showGPTChat, setShowGPTChat] = useState(false);

  return (
    <div className="top-bar">
      <div className="top-bar-left">
        <img src="/header.png" alt="Header" className="header-image" />
      </div> 
      
      <div className="top-bar-center">
        <div className="search-bar">
          <Search className="search-icon" size={16} />
          <input
            type="text"
            className="search-input"
            placeholder="Search mail"
          />
        </div>
      </div>

      <div className="top-bar-right">
        <Sparkles className="topbar-icon" size={18} title="Ask AI" onClick={() => setShowGPTChat(true)} />
        <User className="topbar-icon" size={18} title="Profile" />
        <Settings className="topbar-icon" size={18} title="Settings" />
      </div>

      {showGPTChat && <GPTChat onClose={() => setShowGPTChat(false)} />}
    </div>
  );
};

export default TopBar;
