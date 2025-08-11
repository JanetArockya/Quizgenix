import React, { useState } from 'react';
import './Login.css';

const Login = ({ onLogin }) => {
  const [isLoginMode, setIsLoginMode] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    role: 'student'
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear error when user starts typing
    if (error) setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Form validation
    if (!isLoginMode) {
      if (formData.password !== formData.confirmPassword) {
        setError('Passwords do not match');
        setLoading(false);
        return;
      }
      if (formData.name.length < 2) {
        setError('Name must be at least 2 characters');
        setLoading(false);
        return;
      }
    }

    try {
      const endpoint = isLoginMode ? '/api/login' : '/api/register';
      const payload = isLoginMode 
        ? {
            email: formData.email,
            password: formData.password
          }
        : {
            name: formData.name,
            email: formData.email,
            password: formData.password,
            role: formData.role
          };

      console.log(`🔐 Attempting ${isLoginMode ? 'login' : 'registration'}...`, {
        endpoint,
        email: formData.email
      });

      const response = await fetch(`http://127.0.0.1:5000${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      });

      const data = await response.json();
      console.log('📡 Server response:', data);

      if (response.ok) {
        // Store authentication data
        localStorage.setItem('token', data.token);
        localStorage.setItem('user', JSON.stringify(data.user));
        
        console.log('✅ Authentication successful:', data.user);
        console.log('🔑 Token stored:', data.token.substring(0, 20) + '...');
        
        // Call the parent component's login handler
        onLogin(data.user);
      } else {
        setError(data.error || `${isLoginMode ? 'Login' : 'Registration'} failed`);
        console.error('❌ Authentication failed:', data.error);
      }
    } catch (error) {
      console.error('❌ Network error:', error);
      setError('Network error. Please ensure the backend server is running on port 5000.');
    }

    setLoading(false);
  };

  const switchMode = () => {
    setIsLoginMode(!isLoginMode);
    setError('');
    setFormData({
      name: '',
      email: '',
      password: '',
      confirmPassword: '',
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
            ❌ {error}
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