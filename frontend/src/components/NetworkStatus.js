import React, { useState, useEffect } from 'react';

const NetworkStatus = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [backendStatus, setBackendStatus] = useState('checking');

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Check backend status
    checkBackendStatus();

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const checkBackendStatus = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/', {
        method: 'GET',
        timeout: 5000
      });
      
      if (response.ok) {
        setBackendStatus('connected');
      } else {
        setBackendStatus('error');
      }
    } catch (error) {
      console.error('Backend check failed:', error);
      setBackendStatus('disconnected');
    }
  };

  if (!isOnline) {
    return (
      <div style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        background: '#dc3545',
        color: 'white',
        padding: '10px',
        textAlign: 'center',
        zIndex: 9999
      }}>
        🔌 No internet connection
      </div>
    );
  }

  if (backendStatus === 'disconnected') {
    return (
      <div style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        background: '#ffc107',
        color: '#333',
        padding: '10px',
        textAlign: 'center',
        zIndex: 9999
      }}>
        ⚠️ Backend server disconnected. Please start the backend: <code>python app/main.py</code>
        <button 
          onClick={checkBackendStatus}
          style={{ marginLeft: '10px', padding: '2px 8px' }}
        >
          Retry
        </button>
      </div>
    );
  }

  return null;
};

export default NetworkStatus;