const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:5000';

export const apiConfig = {
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
};

export const apiCall = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  const token = localStorage.getItem('token');
  
  const config = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
      ...options.headers,
    },
  };

  try {
    console.log(`🌐 API Call: ${options.method || 'GET'} ${url}`);
    
    const response = await fetch(url, config);
    
    console.log(`📡 Response: ${response.status} ${response.statusText}`);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Network error' }));
      throw new Error(errorData.error || `HTTP ${response.status}`);
    }
    
    const data = await response.json();
    return data;
    
  } catch (error) {
    console.error(`❌ API Error for ${endpoint}:`, error);
    
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      throw new Error('Cannot connect to server. Please check if the backend is running.');
    }
    
    throw error;
  }
};

export default apiCall;