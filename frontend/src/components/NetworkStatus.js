import React, { useState, useEffect } from 'react';

const NetworkStatus = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [backendStatus, setBackendStatus] = useState('checking');

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    checkBackendStatus();
    const interval = setInterval(checkBackendStatus, 30000); // Check every 30 seconds

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      clearInterval(interval);
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
        zIndex: 9999,
        fontSize: '14px'
      }}>
        🔌 No internet connection - Please check your network
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
        zIndex: 9999,
        fontSize: '14px'
      }}>
        ⚠️ Backend server disconnected. Please start: <code>python app/main.py</code>
        <button 
          onClick={checkBackendStatus}
          style={{ 
            marginLeft: '10px', 
            padding: '5px 10px',
            border: 'none',
            borderRadius: '4px',
            background: '#333',
            color: 'white',
            cursor: 'pointer'
          }}
        >
          Retry Connection
        </button>
      </div>
    );
  }

  return null;
};

export default NetworkStatus;