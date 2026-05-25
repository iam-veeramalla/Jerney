import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
      <Toaster
        position="bottom-right"
        toastOptions={{
          style: {
            background: '#1a1a2e',
            color: '#e0e0ff',
            border: '1px solid rgba(139, 92, 246, 0.3)',
            borderRadius: '16px',
            fontFamily: 'Space Grotesk, sans-serif',
          },
        }}
      />
    </BrowserRouter>
  </React.StrictMode>
);
