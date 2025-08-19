import React, { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

export default function OAuthCallback() {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const init = async () => {
      const params = new URLSearchParams(location.search);
      const token = params.get('access_token');
      const userId = params.get('user_id');

      if (!token || !userId) {
        navigate('/login');
        return;
      }

      localStorage.setItem('authToken', token);
      localStorage.setItem('userId', userId);

      try {
        // Step 1: Trigger Gmail fetch
        const fetchRes = await fetch(`${import.meta.env.VITE_BACKEND_URL}/emails/fetch`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (!fetchRes.ok) throw new Error('Failed to fetch Gmail emails');

        // Step 2: Fetch recent sent emails
        const emailRes = await fetch('http://localhost:8000/api/emails?limit=50&type=sent', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        const raw = await emailRes.json();
        console.log("📬 Raw sent emails response:", raw);

        const emails = Array.isArray(raw) ? raw : raw.emails || [];
        const emailBodies = emails.map(email => email.body).filter(Boolean);


        // Step 3: Initialize user style
        await fetch('http://localhost:8000/api/api/style/init-user-style', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_id: userId,
            emails: emailBodies,
          }),
        });

        console.log('✅ User style initialized from real emails');
      } catch (err) {
        console.error('❌ Failed to init user style:', err);
      }

      navigate('/inbox');
    };

    init();
  }, [location.search, navigate]);

  return <p>Logging in and syncing your emails...</p>;
}
