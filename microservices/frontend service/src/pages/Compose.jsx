import { useState } from 'react';

function Compose() {
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [reply, setReply] = useState('');

  return (
    <div style={{ padding: '2rem', maxWidth: '700px', margin: '0 auto' }}>
      <h2>Compose GPT Reply</h2>

      <label>Subject:</label>
      <input
        type="text"
        value={subject}
        onChange={(e) => setSubject(e.target.value)}
        style={{ width: '100%', padding: '0.5rem', marginBottom: '1rem' }}
      />

      <label>Body:</label>
      <textarea
        value={body}
        onChange={(e) => setBody(e.target.value)}
        rows={6}
        style={{ width: '100%', padding: '0.5rem', marginBottom: '1rem' }}
      />

      <button
        onClick={() => setReply('📬 (GPT suggestion will appear here)')}
        style={{
          padding: '0.6rem 1.2rem',
          backgroundColor: '#007bff',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer',
        }}
      >
        Generate Reply
      </button>

      {reply && (
        <div style={{ marginTop: '2rem', backgroundColor: '#f1f1f1', padding: '1rem' }}>
          <strong>Suggested Reply:</strong>
          <p>{reply}</p>
          <button style={{ marginTop: '1rem' }}>Edit & Save Draft</button>
        </div>
      )}
    </div>
  );
}

export default Compose;
