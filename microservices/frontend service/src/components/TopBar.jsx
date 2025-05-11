import React from 'react';
import { Search, User, Settings } from 'lucide-react';
import './TopBar.css';

const TopBar = () => {
  return (
    <div className="top-bar">
      <div className="top-bar-left" />
      
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
        <User className="topbar-icon" size={18} title="Profile" />
        <Settings className="topbar-icon" size={18} title="Settings" />
      </div>
    </div>
  );
};

export default TopBar;
