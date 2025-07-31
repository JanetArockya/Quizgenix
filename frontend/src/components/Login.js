import React, { useState } from 'react';
import './Login.css';

const Login = ({ onLogin }) => {
  const [isLoginMode, setIsLoginMode] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    name: '',
    role: 'student'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    if (error) setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Validation
    if (!isLoginMode && formData.password !== formData.confirmPassword) {
      setError('Passwords do not match!');
      setLoading(false);
      return;
    }

    if (!isLoginMode && formData.password.length < 6) {
      setError('Password must be at least 6 characters long!');
      setLoading(false);
      return;
    }

    try {
      const endpoint = isLoginMode ? '/api/login' : '/api/register';
      const payload = {
        email: formData.email,
        password: formData.password
      };
      
      if (!isLoginMode) {
        payload.name = formData.name;
        payload.role = formData.role;
      }

      console.log('🔐 Attempting authentication...', { endpoint, email: payload.email });

      const response = await fetch(`http://127.0.0.1:5000${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      const data = await response.json();
      console.log('📡 Server response:', data);

      if (response.ok) {
        console.log('✅ Authentication successful:', data);
        if (data.user && data.token) {
          localStorage.setItem('token', data.token);
          localStorage.setItem('user', JSON.stringify(data.user));
          onLogin(data.user);
        } else {
          setError('Invalid response from server. Please try again.');
        }
      } else {
        setError(data.error || `Server error: ${response.status}`);
      }
    } catch (error) {
      console.error('🚨 Network error:', error);
      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        setError('🔌 Cannot connect to server. Please ensure the backend is running on http://127.0.0.1:5000');
      } else {
        setError('Network error. Please check your connection and try again.');
      }
    }

    setLoading(false);
  };

  const switchMode = () => {
    setIsLoginMode(!isLoginMode);
    setError('');
    setFormData({
      email: '',
      password: '',
      confirmPassword: '',
      name: '',
      role: 'student'
    });
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h1>🧠 Quizgenix</h1>
          <p>AI-Powered Quiz Generation Platform</p>
        </div>

        <div className="auth-tabs">
          <button 
            className={`tab ${isLoginMode ? 'active' : ''}`}
            onClick={() => setIsLoginMode(true)}
          >
            Sign In
          </button>
          <button 
            className={`tab ${!isLoginMode ? 'active' : ''}`}
            onClick={() => setIsLoginMode(false)}
          >
            Sign Up
          </button>
        </div>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="auth-form">
          {!isLoginMode && (
            <div className="form-group">
              <input
                type="text"
                name="name"
                placeholder="Full Name"
                value={formData.name}
                onChange={handleInputChange}
                required
                className="form-input"
                minLength="2"
              />
            </div>
          )}

          <div className="form-group">
            <input
              type="email"
              name="email"
              placeholder="Email Address"
              value={formData.email}
              onChange={handleInputChange}
              required
              className="form-input"
            />
          </div>

          <div className="form-group">
            <input
              type="password"
              name="password"
              placeholder="Password"
              value={formData.password}
              onChange={handleInputChange}
              required
              className="form-input"
              minLength="6"
            />
          </div>

          {!isLoginMode && (
            <>
              <div className="form-group">
                <input
                  type="password"
                  name="confirmPassword"
                  placeholder="Confirm Password"
                  value={formData.confirmPassword}
                  onChange={handleInputChange}
                  required
                  className="form-input"
                  minLength="6"
                />
              </div>

              <div className="form-group">
                <select
                  name="role"
                  value={formData.role}
                  onChange={handleInputChange}
                  className="form-input"
                >
                  <option value="student">🎓 Student</option>
                  <option value="lecturer">👨‍🏫 Lecturer</option>
                </select>
              </div>
            </>
          )}

          <button 
            type="submit" 
            className="auth-button"
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="loading-spinner"></span>
                {isLoginMode ? 'Signing In...' : 'Creating Account...'}
              </>
            ) : (
              isLoginMode ? 'Sign In' : 'Create Account'
            )}
          </button>
        </form>

        <div className="auth-footer">
          <p>
            {isLoginMode ? "Don't have an account? " : "Already have an account? "}
            <button 
              onClick={switchMode}
              className="link-button"
              type="button"
            >
              {isLoginMode ? 'Sign Up' : 'Sign In'}
            </button>
          </p>
          
          <div style={{ 
            marginTop: '20px', 
            padding: '15px', 
            background: '#f8f9fa', 
            borderRadius: '8px', 
            fontSize: '12px',
            border: '1px solid #e9ecef'
          }}>
            <h4 style={{ 
              margin: '0 0 10px 0', 
              color: '#667eea', 
              textAlign: 'center',
              fontSize: '13px',
              fontWeight: '600'
            }}>
              🧪 Test Accounts:
            </h4>
            <p style={{ 
              margin: '5px 0', 
              fontFamily: 'Courier New, monospace',
              background: 'white',
              padding: '4px 8px',
              borderRadius: '4px',
              border: '1px solid #dee2e6'
            }}>
              <strong>Lecturer:</strong> lecturer@test.com / password123
            </p>
            <p style={{ 
              margin: '5px 0', 
              fontFamily: 'Courier New, monospace',
              background: 'white',
              padding: '4px 8px',
              borderRadius: '4px',
              border: '1px solid #dee2e6'
            }}>
              <strong>Student:</strong> student@test.com / password123
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;