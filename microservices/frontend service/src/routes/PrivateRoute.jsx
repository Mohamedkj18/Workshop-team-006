// src/routes/PrivateRoute.jsx
import { Navigate, Outlet } from 'react-router-dom';

export default function PrivateRoute() {
  const isAuthenticated = localStorage.getItem('authToken'); // or use context/state

  return isAuthenticated ? <Outlet /> : <Navigate to="/login" />;
}
