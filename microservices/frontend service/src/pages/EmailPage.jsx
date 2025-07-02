import React, { useEffect, useMemo, useState } from 'react';
import EmailWrapper from '../components/EmailWrapper';
import './styles/Layout.css';

const mockEmails = {
  starred: [/* ... */],
  trash: [/* ... */],
};

export default function EmailPage({ type }) {
  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(type === 'drafts' || type === 'inbox' || type === 'sent');

  useEffect(() => {
  const fetchEmails = async () => {
    try {
      const token = localStorage.getItem("authToken");
      const userId = localStorage.getItem("userId");
      let url = null;
      let headers = {};

      if (type === "drafts") {
        url = `${import.meta.env.VITE_BACKEND_URL}/drafts?user_id=${userId}`;
      } else if (type === "inbox") {
        url = `${import.meta.env.VITE_BACKEND_URL}/emails?skip=0&limit=50&type=Inbox`;
        headers["Authorization"] = `Bearer ${token}`;
      }
      else if (type === "sent") {
        url = `${import.meta.env.VITE_BACKEND_URL}/emails?skip=0&limit=50&type=Sent`;
        headers["Authorization"] = `Bearer ${token}`;
      } else if (type === "starred") {
        url = `${import.meta.env.VITE_BACKEND_URL}/emails?skip=0&limit=50&type=Starred`;
        headers["Authorization"] = `Bearer ${token}`;
      } else if (type === "trash") {
        url = `${import.meta.env.VITE_BACKEND_URL}/emails?skip=0&limit=50&type=Trash`;
        headers["Authorization"] = `Bearer ${token}`;
      }

      if (url) {
        const res = await fetch(url, { headers });
        const data = await res.json();
        console.log(`${type} fetched:`, data);

        if (type === "drafts") {
          setEmails(data.items || []);
        } else if (type === "inbox" || type === "sent" || type === "starred" || type === "trash") {
          setEmails(data.emails || []);
        }
      } else {
        setEmails([]);
      }
    } catch (err) {
      console.error(`Failed to load ${type}:`, err);
      setEmails([]);
    } finally {
      setLoading(false);
    }
  };

  fetchEmails();
}, [type]);

  const emailsToShow = useMemo(() => emails, [emails]);

  return (
    <div className="content-area">
      <div className="email-list-wrapper">
        {loading ? (
            <p>Loading {type}...</p>
        ) : Array.isArray(emailsToShow) ? (
            <EmailWrapper emails={emailsToShow} type={type} />
        ) : (
            <p>Something went wrong loading emails.</p>
        )}
      </div>
    </div>
  );
}
