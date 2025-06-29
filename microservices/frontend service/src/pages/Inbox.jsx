import React from 'react';
import EmailList from '../components/EmailList';
import './styles/Layout.css';

export default function Inbox() {
  return (
    <div className="content-area">
      <div className="email-list-wrapper">
        <EmailList />
      </div>
    </div>
  );
}
