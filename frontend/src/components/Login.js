import React, { useState, useEffect } from 'react';
import './Login.css';

const Login = ({ onLogin }) => {
  const [isLoginMode, setIsLoginMode] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    role: 'student'
  });

  // Clear messages after 5 seconds
  useEffect(() => {
    if (error || success) {
      const timer = setTimeout(() => {
        setError('');
        setSuccess('');
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [error, success]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear error when user starts typing
    if (error) setError('');
  };

  const handleRoleSelect = (role) => {
    setFormData(prev => ({
      ...prev,
      role
    }));
  };

  const toggleMode = () => {
    setIsLoginMode(!isLoginMode);
    setError('');
    setSuccess('');
    setFormData({
      name: '',
      email: '',
      password: '',
      confirmPassword: '',
      role: 'student'
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

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
      if (formData.password.length < 6) {
        setError('Password must be at least 6 characters');
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

  // eslint-disable-next-line no-unused-vars
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
          <div className="logo-icon">🧠</div>
          <h1>Quizgenix</h1>
          <p>AI-Powered Quiz Generation Platform</p>
        </div>

        <div className="auth-tabs">
          <button 
            className={`tab ${isLoginMode ? 'active' : ''}`}
            onClick={toggleMode}
            type="button"
          >
            Sign In
          </button>
          <button 
            className={`tab ${!isLoginMode ? 'active' : ''}`}
            onClick={toggleMode}
            type="button"
          >
            Sign Up
          </button>
        </div>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        {success && (
          <div className="success-message">
            {success}
          </div>
        )}

        <form onSubmit={handleSubmit} className={`auth-form ${loading ? 'form-loading' : ''}`}>
          {!isLoginMode && (
            <div className="form-group">
              <label className="form-label">Full Name</label>
              <input
                type="text"
                name="name"
                placeholder="Enter your full name"
                value={formData.name}
                onChange={handleInputChange}
                required
                className="form-input"
                minLength="2"
              />
            </div>
          )}

          <div className="form-group">
            <label className="form-label">Email Address</label>
            <input
              type="email"
              name="email"
              placeholder="Enter your email"
              value={formData.email}
              onChange={handleInputChange}
              required
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <div className="password-input-container">
              <input
                type={showPassword ? "text" : "password"}
                name="password"
                placeholder="Enter your password"
                value={formData.password}
                onChange={handleInputChange}
                required
                className="form-input"
                minLength="6"
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? '🙈' : '👁️'}
              </button>
            </div>
          </div>

          {!isLoginMode && (
            <>
              <div className="form-group">
                <label className="form-label">Confirm Password</label>
                <input
                  type="password"
                  name="confirmPassword"
                  placeholder="Confirm your password"
                  value={formData.confirmPassword}
                  onChange={handleInputChange}
                  required
                  className="form-input"
                  minLength="6"
                />
              </div>

              <div className="form-group">
                <label className="form-label">Select Your Role</label>
                <div className="role-selector">
                  <div 
                    className={`role-option ${formData.role === 'student' ? 'selected' : ''}`}
                    onClick={() => handleRoleSelect('student')}
                  >
                    <span className="role-icon">🎓</span>
                    <div>Student</div>
                  </div>
                  <div 
                    className={`role-option ${formData.role === 'lecturer' ? 'selected' : ''}`}
                    onClick={() => handleRoleSelect('lecturer')}
                  >
                    <span className="role-icon">👨‍🏫</span>
                    <div>Lecturer</div>
                  </div>
                </div>
              </div>
            </>
          )}

          <button 
            type="submit" 
            className="auth-button"
          >
            {loading ? (
              <div className="loading-btn">
                <span className="loading-spinner"></span>
                {isLoginMode ? 'Signing In...' : 'Creating Account...'}
              </div>
            ) : (
              <>
                {isLoginMode ? '🚀 Sign In' : '✨ Create Account'}
              </>
            )}
          </button>
        </form>

        <div className="auth-footer">
          <p>
            {isLoginMode ? "Don't have an account? " : "Already have an account? "}
            <button 
              onClick={toggleMode}
              className="link-button"
              type="button"
            >
              {isLoginMode ? 'Sign Up' : 'Sign In'}
            </button>
          </p>
          
          {isLoginMode && (
            <div className="forgot-password">
              {/* eslint-disable-next-line jsx-a11y/anchor-is-valid */}
              <a href="#" onClick={(e) => e.preventDefault()}>
                Forgot your password?
              </a>
            </div>
          )}
        </div>

        {/* Demo credentials helper */}
        {process.env.NODE_ENV === 'development' && (
          <div style={{ 
            marginTop: '20px', 
            padding: '15px', 
            background: 'rgba(255, 255, 255, 0.1)', 
            borderRadius: '12px', 
            fontSize: '12px',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            backdropFilter: 'blur(10px)'
          }}>
            <h4 style={{ 
              margin: '0 0 10px 0', 
              color: 'rgba(255, 255, 255, 0.9)', 
              textAlign: 'center',
              fontSize: '13px',
              fontWeight: '600'
            }}>
              🔧 Demo Credentials
            </h4>
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: '1fr 1fr', 
              gap: '10px',
              color: 'rgba(255, 255, 255, 0.8)'
            }}>
              <div>
                <strong>Student:</strong><br/>
                Email: student@test.com<br/>
                Password: password
              </div>
              <div>
                <strong>Lecturer:</strong><br/>
                Email: lecturer@test.com<br/>
                Password: password
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Login;