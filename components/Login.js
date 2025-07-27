import React, { useState } from 'react';
import './Login.css';
import { GoogleLogin } from '@react-oauth/google';

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
    // Clear error when user starts typing
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

      console.log('Sending request to:', `http://127.0.0.1:5000${endpoint}`);
      console.log('Payload:', payload);

      const response = await fetch(`http://127.0.0.1:5000${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      const data = await response.json();
      console.log('Response:', data);

      if (response.ok && data.user && data.token) {
        // Store authentication data
        localStorage.setItem('token', data.token);
        localStorage.setItem('user', JSON.stringify(data.user));
        
        // Call onLogin with user data
        onLogin(data.user);
      } else {
        setError(data.error || 'Authentication failed. Please try again.');
      }
    } catch (error) {
      console.error('Network error:', error);
      setError('Network error. Please check your connection and try again.');
    }

    setLoading(false);
  };

  const handleGoogleSuccess = async (credentialResponse) => {
    try {
      const response = await fetch('http://localhost:5000/api/auth/google', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token: credentialResponse.credential
        })
      });

      const data = await response.json();
      
      if (response.ok) {
        localStorage.setItem('token', data.token);
        localStorage.setItem('user', JSON.stringify(data.user));
        onLogin(data.user);
      } else {
        setError(data.error || 'Google login failed');
      }
    } catch (error) {
      console.error('Google login error:', error);
      setError('Google login failed');
    }
  };

  const handleGoogleLogin = () => {
    alert('Google OAuth integration coming soon!');
  };

  return (
    <div className="login-page">
      <div className="login-background">
        <div className="floating-shapes">
          <div className="shape shape-1"></div>
          <div className="shape shape-2"></div>
          <div className="shape shape-3"></div>
          <div className="shape shape-4"></div>
          <div className="shape shape-5"></div>
        </div>
      </div>

      <div className="login-card">
        <div className="login-header">
          <h1 className="login-title">
            <span className="quiz-text">Quiz</span>
            <span className="genix-text">genix</span>
          </h1>
          <p className="login-subtitle">
            {isLoginMode ? 'Welcome back!' : 'Create your account'}
          </p>
        </div>

        <div className="auth-tabs">
          <button 
            className={`tab-btn ${isLoginMode ? 'active' : ''}`}
            onClick={() => {
              setIsLoginMode(true);
              setError('');
              setFormData({ ...formData, confirmPassword: '', name: '' });
            }}
          >
            Login
          </button>
          <button 
            className={`tab-btn ${!isLoginMode ? 'active' : ''}`}
            onClick={() => {
              setIsLoginMode(false);
              setError('');
            }}
          >
            Sign Up
          </button>
        </div>

        {error && (
          <div className="error-message">
            ⚠️ {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="login-form">
          {!isLoginMode && (
            <div className="form-group">
              <label htmlFor="name">Full Name</label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                required={!isLoginMode}
                placeholder="Enter your full name"
              />
            </div>
          )}

          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              required
              placeholder="Enter your email"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              required
              placeholder="Enter your password"
            />
          </div>

          {!isLoginMode && (
            <>
              <div className="form-group">
                <label htmlFor="confirmPassword">Confirm Password</label>
                <input
                  type="password"
                  id="confirmPassword"
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleInputChange}
                  required
                  placeholder="Confirm your password"
                />
              </div>

              <div className="form-group">
                <label htmlFor="role">Role</label>
                <select
                  id="role"
                  name="role"
                  value={formData.role}
                  onChange={handleInputChange}
                  className="role-select"
                >
                  <option value="student">Student</option>
                  <option value="lecturer">Lecturer/Educator</option>
                </select>
              </div>
            </>
          )}

          <button 
            type="submit" 
            className="login-btn"
            disabled={loading}
          >
            {loading ? (
              <div className="loading-spinner-small"></div>
            ) : (
              isLoginMode ? 'Login' : 'Sign Up'
            )}
          </button>
        </form>

        <div className="divider">
          <span>or</span>
        </div>

        <div className="google-login-section">
          <GoogleLogin
            onSuccess={handleGoogleSuccess}
            onError={() => setError('Google login failed')}
            text="signin_with"
            theme="outline"
            size="large"
          />
        </div>

        <div className="demo-accounts">
          <p className="demo-title">Quick Test Accounts:</p>
          <div className="demo-account">
            <strong>Lecturer:</strong> lecturer@test.com / password123
          </div>
          <div className="demo-account">
            <strong>Student:</strong> student@test.com / password123
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
