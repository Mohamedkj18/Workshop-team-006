import { Link } from 'react-router-dom';

function Navbar() {
  return (
    <nav style={{ 
      display: 'flex', 
      gap: '1rem', 
      padding: '1rem', 
      borderBottom: '1px solid #ddd', 
      backgroundColor: '#f9f9f9' 
    }}>
      <Link to="/" style={{ textDecoration: 'none' }}>📥 Inbox</Link>
      <Link to="/compose" style={{ textDecoration: 'none' }}>✍️ Compose</Link>
      <Link to="/drafts" style={{ textDecoration: 'none' }}>📄 Drafts</Link>
    </nav>
  );
}

export default Navbar;
