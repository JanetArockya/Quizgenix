import React, { useState } from 'react';
import './Login.css';
import apiCall from '../config/api';

const Login = ({ onLogin }) => {
  const [isLoginMode, setIsLoginMode] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    role: 'student',
    name: ''
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

    if (!isLoginMode && formData.password !== formData.confirmPassword) {
      setError('Passwords do not match!');
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

      console.log('🔐 Attempting authentication...');

      const data = await apiCall(endpoint, {
        method: 'POST',
        body: JSON.stringify(payload),
      });

      console.log('✅ Authentication successful:', data);

      if (data.user && data.token) {
        localStorage.setItem('token', data.token);
        localStorage.setItem('user', JSON.stringify(data.user));
        onLogin(data.user);
      } else {
        setError('Authentication failed. Please try again.');
      }

    } catch (error) {
      console.error('🚨 Authentication error:', error);
      
      if (error.message.includes('Cannot connect to server')) {
        setError('🔌 Cannot connect to server. Please ensure the backend is running on http://127.0.0.1:5000');
      } else if (error.message.includes('Network error')) {
        setError('🌐 Network error. Please check your internet connection.');
      } else {
        setError(error.message || 'Authentication failed. Please try again.');
      }
    }

    setLoading(false);
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h1>🧠 Quizgenix</h1>
          <p>Smart Quiz Generation Platform</p>
        </div>

        <div className="auth-tabs">
          <button 
            className={`tab ${isLoginMode ? 'active' : ''}`}
            onClick={() => setIsLoginMode(true)}
          >
            Login
          </button>
          <button 
            className={`tab ${!isLoginMode ? 'active' : ''}`}
            onClick={() => setIsLoginMode(false)}
          >
            Register
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
                required={!isLoginMode}
                className="form-input"
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
                  required={!isLoginMode}
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <select
                  name="role"
                  value={formData.role}
                  onChange={handleInputChange}
                  className="form-input"
                >
                  <option value="student">Student</option>
                  <option value="lecturer">Lecturer</option>
                </select>
              </div>
            </>
          )}

          <button 
            type="submit" 
            className="auth-button"
            disabled={loading}
          >
            {loading ? 'Processing...' : (isLoginMode ? 'Login' : 'Register')}
          </button>
        </form>

        <div className="auth-footer">
          {isLoginMode ? (
            <p>Don't have an account? <button onClick={() => setIsLoginMode(false)} className="link-button">Register here</button></p>
          ) : (
            <p>Already have an account? <button onClick={() => setIsLoginMode(true)} className="link-button">Login here</button></p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Login;