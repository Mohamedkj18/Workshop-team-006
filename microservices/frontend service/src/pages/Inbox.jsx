import { useState } from 'react';
import EmailList from '../components/EmailList';
import EmailView from '../components/EmailView';

export default function Inbox() {
  const [selectedEmail, setSelectedEmail] = useState(null);

  return (
    <div className="inbox-container">
      {selectedEmail ? (
        <EmailView
          email={selectedEmail}
          onBack={() => setSelectedEmail(null)}
        />
      ) : (
        <EmailList onSelectEmail={setSelectedEmail} />
      )}
    </div>
  );
}
