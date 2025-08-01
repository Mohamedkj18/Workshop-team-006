import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import { UserProvider } from './context/UserContext';
import { BrowserRouter } from 'react-router-dom';

ReactDOM.createRoot(document.getElementById('root')).render(
  <BrowserRouter key={Date.now()}> 
    <UserProvider>
      <App />
    </UserProvider>
  </BrowserRouter>
);
