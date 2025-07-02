import { Routes, Route, Navigate } from 'react-router-dom';
import AppLayout from './layout/AppLayout';
import PrivateRoute from './routes/PrivateRoute';

import Home from './pages/Home';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Learning from './pages/Learning';
import Onboarding from './pages/Onboarding';
import Inbox from './pages/Inbox';
import Drafts from './pages/Drafts';
import Sent from './pages/Sent';
import Starred from './pages/Starred';
import Trash from './pages/Trash';
import OAuthCallback from './pages/OAuthCallback'; // NEW

export default function App() {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />
      <Route path="/learning" element={<Learning />} />
      <Route path="/onboarding" element={<Onboarding />} />
      <Route path="/auth/callback" element={<OAuthCallback />} /> {/* NEW */}

      {/* Protected routes */}
      <Route element={<PrivateRoute />}>
        <Route element={<AppLayout />}>
          <Route path="/inbox" element={<Inbox />} />
          <Route path="/drafts" element={<Drafts />} />
          <Route path="/sent" element={<Sent />} />
          <Route path="/starred" element={<Starred />} />
          <Route path="/trash" element={<Trash />} />
        </Route>
      </Route>

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}
