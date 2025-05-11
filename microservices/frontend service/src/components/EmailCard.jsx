function EmailCard({ email, onSelect }) {
    return (
      <div
        onClick={() => onSelect(email)}
        style={{
          border: '1px solid #ccc',
          borderRadius: '8px',
          padding: '1rem',
          marginBottom: '1rem',
          cursor: 'pointer',
          backgroundColor: '#fff',
          boxShadow: '0 1px 4px rgba(0,0,0,0.05)',
        }}
      >
        <h3 style={{ margin: 0 }}>{email.subject}</h3>
        <p style={{ color: '#555' }}>{email.body.slice(0, 100)}...</p>
        <small style={{ color: '#999' }}>From: {email.sender}</small>
      </div>
    );
  }
  
  export default EmailCard;
  