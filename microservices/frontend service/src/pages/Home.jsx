import { Link } from 'react-router-dom';

function Home() {
  return (
    <div style={{
      textAlign: 'center',
      marginTop: '5rem',
      padding: '2rem'
    }}>
      <h1>📨 AI Email Assistant</h1>
      <p style={{ maxWidth: '500px', margin: '1rem auto', fontSize: '1.1rem' }}>
        Welcome! This app helps you respond to emails quickly and professionally using AI. 
        You can view your inbox, generate smart replies, and save drafts — all in one place.
      </p>
      <Link to="/inbox">
        <button style={{
          padding: '0.8rem 1.6rem',
          fontSize: '1rem',
          backgroundColor: '#007bff',
          color: '#fff',
          border: 'none',
          borderRadius: '6px',
          cursor: 'pointer',
          marginTop: '1rem'
        }}>
          Go to Inbox
        </button>
      </Link>
    </div>
  );
}

export default Home;
