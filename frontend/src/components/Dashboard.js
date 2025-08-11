import React, { useState, useEffect } from 'react';
import './Dashboard.css';

const Dashboard = ({ user, onLogout }) => {
  const [activeTab, setActiveTab] = useState(user.role === 'lecturer' ? 'create' : 'available');
  const [quizzes, setQuizzes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [showPreview, setShowPreview] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    subject: '',
    topic: '',
    difficulty: 'medium',
    questionCount: 5
  });

  const handleCreateQuiz = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      const token = localStorage.getItem('token');
      console.log('🔑 Using token:', token ? token.substring(0, 20) + '...' : 'No token found');
      
      if (!token) {
        setMessage('❌ No authentication token found. Please login again.');
        setLoading(false);
        return;
      }

      const response = await fetch('http://127.0.0.1:5000/api/quiz', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          ...formData,
          questionCount: parseInt(formData.questionCount)
        })
      });

      console.log('📡 Response status:', response.status);
      const data = await response.json();
      console.log('📡 Response data:', data);
      
      if (response.ok) {
        setMessage('✅ Quiz created successfully!');
        setFormData({
          title: '',
          subject: '',
          topic: '',
          difficulty: 'medium',
          questionCount: 5
        });
        fetchQuizzes();
        setTimeout(() => setMessage(''), 3000);
        
        // Auto-show preview of newly created quiz
        setTimeout(() => {
          setShowPreview(data);
        }, 1000);
      } else {
        if (response.status === 401) {
          setMessage('❌ Authentication failed. Please login again.');
        } else {
          setMessage(`❌ Error: ${data.error || 'Failed to create quiz'}`);
        }
      }
    } catch (error) {
      console.error('❌ Network error:', error);
      setMessage('❌ Network error. Please ensure backend is running.');
    }

    setLoading(false);
  };

  const fetchQuizzes = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://127.0.0.1:5000/api/quizzes', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      const data = await response.json();
      if (response.ok) {
        setQuizzes(data.quizzes);
      }
    } catch (error) {
      console.error('Failed to fetch quizzes:', error);
    }
  };

  const handleDownload = async (quiz, format) => {
    try {
      const token = localStorage.getItem('token');
      setMessage(`📄 Generating ${format.toUpperCase()} download...`);

      const response = await fetch(`http://127.0.0.1:5000/api/quiz/${quiz.id}/download/${format}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${quiz.title.replace(/[^a-zA-Z0-9]/g, '_')}.${format}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        setMessage(`✅ ${format.toUpperCase()} downloaded successfully!`);
        setTimeout(() => setMessage(''), 3000);
      } else {
        setMessage(`❌ Failed to download ${format.toUpperCase()}`);
      }
    } catch (error) {
      console.error('Download error:', error);
      setMessage(`❌ Download error: ${error.message}`);
    }
  };

  useEffect(() => {
    fetchQuizzes();
  }, []);

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>🧠 Quizgenix Dashboard</h1>
        <div className="user-info">
          <span>Welcome, {user.name} ({user.role})</span>
          <button onClick={onLogout} className="logout-btn">Logout</button>
        </div>
      </header>

      <div className="dashboard-content">
        <nav className="dashboard-nav">
          {user.role === 'lecturer' && (
            <button
              className={`nav-btn ${activeTab === 'create' ? 'active' : ''}`}
              onClick={() => setActiveTab('create')}
            >
              📝 Create Quiz
            </button>
          )}
          <button
            className={`nav-btn ${activeTab === 'available' ? 'active' : ''}`}
            onClick={() => setActiveTab('available')}
          >
            📚 My Quizzes ({quizzes.length})
          </button>
        </nav>

        <div className="dashboard-main">
          {message && (
            <div className={`message ${message.includes('✅') ? 'success' : 'error'}`}>
              {message}
            </div>
          )}

          {activeTab === 'create' && user.role === 'lecturer' && (
            <div className="create-quiz">
              <h2>🎯 Create New Quiz</h2>
              <div className="ai-badge">
                <span>🤖 AI-Powered Question Generation</span>
              </div>
              <form onSubmit={handleCreateQuiz} className="quiz-form">
                <input
                  type="text"
                  placeholder="Quiz Title (e.g., JavaScript Fundamentals)"
                  value={formData.title}
                  onChange={(e) => setFormData({...formData, title: e.target.value})}
                  required
                />
                <input
                  type="text"
                  placeholder="Subject (e.g., Computer Science)"
                  value={formData.subject}
                  onChange={(e) => setFormData({...formData, subject: e.target.value})}
                  required
                />
                <input
                  type="text"
                  placeholder="Topic (e.g., Variables, Functions, Loops)"
                  value={formData.topic}
                  onChange={(e) => setFormData({...formData, topic: e.target.value})}
                  required
                />
                <select
                  value={formData.difficulty}
                  onChange={(e) => setFormData({...formData, difficulty: e.target.value})}
                >
                  <option value="easy">🟢 Easy - Basic concepts</option>
                  <option value="medium">🟡 Medium - Intermediate level</option>
                  <option value="hard">🔴 Hard - Advanced concepts</option>
                </select>
                <select
                  value={formData.questionCount}
                  onChange={(e) => setFormData({...formData, questionCount: e.target.value})}
                >
                  <option value="5">5 Questions</option>
                  <option value="10">10 Questions</option>
                  <option value="15">15 Questions</option>
                  <option value="20">20 Questions</option>
                </select>
                <button type="submit" disabled={loading} className="create-btn">
                  {loading ? (
                    <>
                      <span className="loading-spinner"></span>
                      🤖 Generating AI Questions...
                    </>
                  ) : (
                    '🎯 Generate Quiz with AI'
                  )}
                </button>
              </form>
            </div>
          )}

          {activeTab === 'available' && (
            <div className="quiz-list">
              <h2>📚 My Quizzes ({quizzes.length})</h2>
              {quizzes.length > 0 ? (
                <div className="quizzes-grid">
                  {quizzes.map(quiz => (
                    <div key={quiz.id} className="quiz-card">
                      <div className="quiz-header">
                        <h3>{quiz.title}</h3>
                        <span className={`difficulty-badge ${quiz.difficulty}`}>
                          {quiz.difficulty === 'easy' ? '🟢' : quiz.difficulty === 'medium' ? '🟡' : '🔴'} {quiz.difficulty}
                        </span>
                      </div>
                      
                      <div className="quiz-info">
                        <p><strong>📖 Subject:</strong> {quiz.subject}</p>
                        <p><strong>🎯 Topic:</strong> {quiz.topic}</p>
                        <p><strong>❓ Questions:</strong> {quiz.questions?.length || 0}</p>
                        <p><strong>📅 Created:</strong> {new Date(quiz.created_at).toLocaleDateString()}</p>
                      </div>

                      <div className="quiz-actions">
                        <button
                          className="action-btn preview"
                          onClick={() => setShowPreview(quiz)}
                        >
                          👁️ View Quiz
                        </button>
                        <button
                          className="action-btn download pdf"
                          onClick={() => handleDownload(quiz, 'pdf')}
                        >
                          📄 PDF
                        </button>
                        <button
                          className="action-btn download word"
                          onClick={() => handleDownload(quiz, 'docx')}
                        >
                          📝 Word
                        </button>
                        <button
                          className="action-btn download excel"
                          onClick={() => handleDownload(quiz, 'xlsx')}
                        >
                          📊 Excel
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="empty-state">
                  <div className="empty-icon">📝</div>
                  <h3>No Quizzes Yet</h3>
                  <p>Create your first AI-powered quiz using the 'Create Quiz' tab!</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Quiz Preview Modal */}
      {showPreview && (
        <div className="modal-overlay" onClick={() => setShowPreview(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>🎯 Quiz Preview: {showPreview.title}</h2>
              <button
                className="close-btn"
                onClick={() => setShowPreview(null)}
              >
                ×
              </button>
            </div>
            
            <div className="modal-body">
              <div className="quiz-meta">
                <div className="meta-item">
                  <strong>📖 Subject:</strong> {showPreview.subject}
                </div>
                <div className="meta-item">
                  <strong>🎯 Topic:</strong> {showPreview.topic}
                </div>
                <div className="meta-item">
                  <strong>📊 Difficulty:</strong> 
                  <span className={`difficulty-badge ${showPreview.difficulty}`}>
                    {showPreview.difficulty === 'easy' ? '🟢' : showPreview.difficulty === 'medium' ? '🟡' : '🔴'} {showPreview.difficulty}
                  </span>
                </div>
                <div className="meta-item">
                  <strong>❓ Questions:</strong> {showPreview.questions?.length}
                </div>
              </div>

              <div className="questions-container">
                <h3>📝 Questions & Answers:</h3>
                {showPreview.questions?.map((question, index) => (
                  <div key={index} className="question-item">
                    <h4>Q{index + 1}: {question.question}</h4>
                    <div className="options-list">
                      {question.options?.map((option, optIndex) => (
                        <div 
                          key={optIndex} 
                          className={`option ${optIndex === question.correct_answer ? 'correct' : ''}`}
                        >
                          <span className="option-letter">{String.fromCharCode(65 + optIndex)})</span>
                          <span className="option-text">{option}</span>
                          {optIndex === question.correct_answer && <span className="correct-indicator">✅ Correct</span>}
                        </div>
                      ))}
                    </div>
                    <div className="explanation">
                      <strong>💡 Explanation:</strong> {question.explanation}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="modal-footer">
              <div className="download-actions">
                <button
                  className="download-btn pdf"
                  onClick={() => handleDownload(showPreview, 'pdf')}
                >
                  📄 Download PDF
                </button>
                <button
                  className="download-btn word"
                  onClick={() => handleDownload(showPreview, 'docx')}
                >
                  📝 Download Word
                </button>
                <button
                  className="download-btn excel"
                  onClick={() => handleDownload(showPreview, 'xlsx')}
                >
                  📊 Download Excel
                </button>
              </div>
              <button
                className="close-modal-btn"
                onClick={() => setShowPreview(null)}
              >
                Close Preview
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;