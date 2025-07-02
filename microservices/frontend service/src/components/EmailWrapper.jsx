import React, { useState } from 'react';
import EmailList from './EmailList';
import EmailView from './EmailView';
import ComposePopup from './ComposePopup';
import './styles/EmailWrapper.css';

// Centralized config for mailbox type logic
const mailboxTypeConfig = {
    inbox: {
        showStar: true,
        showTrash: true,
        showDelete: false,
        showReply: true,
        showForward: true,
        showRestore: false,
        showCompose: false,
        handlers: ['onStar', 'onTrash'],
    },
    sent: {
        showStar: false,
        showTrash: true,
        showDelete: false,
        showReply: false,
        showForward: true,
        showRestore: false,
        showCompose: false,
        handlers: ['onTrash'],
    },
    drafts: {
        showStar: false,
        showTrash: true,
        showDelete: true,
        showReply: false,
        showForward: false,
        showRestore: false,
        showCompose: true,
        handlers: ['onTrash', 'onDelete'],
    },
    starred: {
        showStar: true,
        showTrash: true,
        showDelete: false,
        showReply: true,
        showForward: true,
        showRestore: false,
        showCompose: false,
        handlers: ['onStar', 'onTrash'],
    },
    trash: {
        showStar: false,
        showTrash: false,
        showDelete: true,
        showReply: false,
        showForward: false,
        showRestore: true,
        showCompose: false,
        handlers: ['onDelete', 'onRestore'],
    },
};

export default function EmailWrapper({ emails: initialEmails = [], type }) {
    const [emails, setEmails] = useState(initialEmails);
    const [selectedEmail, setSelectedEmail] = useState(null);
    const [starred, setStarred] = useState(new Set(
        initialEmails.filter(e => e.starred).map(e => e.id)
    ));
    const [trashed, setTrashed] = useState(new Set(
        initialEmails.filter(e => e.trashed).map(e => e.id)
    ));
    const [composeDraft, setComposeDraft] = useState(null);

    // Toggle star
    const toggleStar = (id) => {
        setStarred(prev => {
            const updated = new Set(prev);
            updated.has(id) ? updated.delete(id) : updated.add(id);
            return updated;
        });
        setEmails(prev =>
            prev.map(email =>
                email.id === id ? { ...email, starred: !email.starred } : email
            )
        );
    };

    // Move to trash
    const moveToTrash = (id) => {
        setTrashed(prev => {
            const updated = new Set(prev);
            updated.add(id);
            return updated;
        });
        setEmails(prev =>
            prev.map(email =>
                email.id === id ? { ...email, trashed: true } : email
            )
        );
        if (selectedEmail && selectedEmail.id === id) setSelectedEmail(null);
    };

    // Restore from trash
    const restoreEmail = (id) => {
        setTrashed(prev => {
            const updated = new Set(prev);
            updated.delete(id);
            return updated;
        });
        setEmails(prev =>
            prev.map(email =>
                email.id === id ? { ...email, trashed: false } : email
            )
        );
        if (selectedEmail && selectedEmail.id === id) setSelectedEmail(null);
    };

    // Permanently delete
    const deleteEmail = (id) => {
        setEmails(prev => prev.filter(email => email.id !== id));
        setStarred(prev => {
            const updated = new Set(prev);
            updated.delete(id);
            return updated;
        });
        setTrashed(prev => {
            const updated = new Set(prev);
            updated.delete(id);
            return updated;
        });
        if (selectedEmail && selectedEmail.id === id) setSelectedEmail(null);
    };

    // Filter emails based on type
    let filteredEmails = emails;
    if (type === 'inbox') {
        filteredEmails = emails.filter(e => !e.trashed);
    } else if (type === 'sent') {
        filteredEmails = emails.filter(e => !e.trashed);
    } else if (type === 'drafts') {
        filteredEmails = emails.filter(e => !e.trashed);
    } else if (type === 'starred') {
        filteredEmails = emails.filter(e => starred.has(e.id) && !e.trashed);
    } else if (type === 'trash') {
        filteredEmails = emails.filter(e => trashed.has(e.id));
    }

    // Handler map for passing only needed handlers
    const handlerMap = {
        onStar: toggleStar,
        onTrash: moveToTrash,
        onDelete: deleteEmail,
        onRestore: restoreEmail,
        onSelectEmail: (email) => {
            if (type === 'drafts') {
                setComposeDraft(email);
            } else {
                setSelectedEmail(email);
            }
        },
    };

    // Only pass handlers needed for this type
    const config = mailboxTypeConfig[type] || {};
    const listHandlers = {};
    (config.handlers || []).forEach(h => {
        listHandlers[h] = handlerMap[h];
    });
    listHandlers.onSelectEmail = handlerMap.onSelectEmail;

    return (
        <div className="email-wrapper rounded-box">
            {composeDraft && (
                <ComposePopup
                    draft={composeDraft}
                    onClose={() => setComposeDraft(null)}
                />
            )}
            {selectedEmail ? (
                <EmailView
                    email={selectedEmail}
                    onBack={() => setSelectedEmail(null)}
                    onStar={config.showStar ? () => toggleStar(selectedEmail.id) : undefined}
                    onTrash={config.showTrash ? () => moveToTrash(selectedEmail.id) : undefined}
                    onDelete={config.showDelete ? () => deleteEmail(selectedEmail.id) : undefined}
                    onRestore={config.showRestore ? () => restoreEmail(selectedEmail.id) : undefined}
                    type={type}
                />
            ) : (
                <EmailList
                    emails={filteredEmails}
                    starred={starred}
                    trashed={trashed}
                    type={type}
                    {...listHandlers}
                />
            )}
        </div>
    );
}
