import React, { useState, useEffect } from 'react';
import './Dashboard.css';

const Dashboard = ({ user, onLogout }) => {
  // State management - MISSING in your current file
  const [activeTab, setActiveTab] = useState('create');
  const [quizzes, setQuizzes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    title: '',
    subject: '',
    topic: '',
    difficulty: 'medium',
    questionCount: '10'
  });
  const [currentQuiz, setCurrentQuiz] = useState(null);
  const [showPreview, setShowPreview] = useState(false);
  const [editingQuestion, setEditingQuestion] = useState(null);

  // Load user's quizzes on component mount
  useEffect(() => {
    if (user?.role === 'lecturer') {
      loadQuizzes();
    }
  }, [user]);

  // API Functions
  const loadQuizzes = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://127.0.0.1:5000/api/quizzes', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setQuizzes(data.quizzes || []);
      } else {
        console.error('Failed to load quizzes');
      }
    } catch (error) {
      console.error('Error loading quizzes:', error);
    }
  };

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    if (error) setError('');
  };

  const handleCreateQuiz = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://127.0.0.1:5000/api/quiz', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (response.ok) {
        setCurrentQuiz(data);
        setShowPreview(true);
        setActiveTab('manage');
        await loadQuizzes(); // Refresh quiz list
        
        // Reset form
        setFormData({
          title: '',
          subject: '',
          topic: '',
          difficulty: 'medium',
          questionCount: '10'
        });
      } else {
        setError(data.error || 'Failed to create quiz');
      }
    } catch (error) {
      setError('Network error. Please ensure the backend is running.');
      console.error('Error creating quiz:', error);
    }

    setLoading(false);
  };

  const handleDownload = async (quizId, format) => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await fetch(`http://127.0.0.1:5000/api/quiz/${quizId}/download/${format}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `quiz.${format === 'word' ? 'docx' : format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        setError('Failed to download file');
      }
    } catch (error) {
      setError('Download failed');
      console.error('Download error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleEditQuestion = (question, index) => {
    setEditingQuestion({ ...question, index });
  };

  const handleSaveQuestion = async (updatedQuestion) => {
    if (currentQuiz) {
      const updatedQuestions = [...currentQuiz.questions];
      updatedQuestions[updatedQuestion.index] = {
        question: updatedQuestion.question,
        options: updatedQuestion.options,
        correct_answer: updatedQuestion.correct_answer
      };

      const updatedQuiz = { ...currentQuiz, questions: updatedQuestions };
      setCurrentQuiz(updatedQuiz);

      // Save to backend
      try {
        const token = localStorage.getItem('token');
        await fetch(`http://127.0.0.1:5000/api/quiz/${currentQuiz.id}/save`, {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            questions: updatedQuestions
          })
        });
        
        await loadQuizzes(); // Refresh quiz list
      } catch (error) {
        console.error('Error saving question:', error);
      }
    }
    setEditingQuestion(null);
  };

  // Modal Components
  const QuizPreview = () => {
    if (!showPreview || !currentQuiz) return null;

    return (
      <div className="modal-overlay" onClick={() => setShowPreview(false)}>
        <div className="modal-content" onClick={e => e.stopPropagation()}>
          <div className="modal-header">
            <h2>📋 Quiz Preview: {currentQuiz.title}</h2>
            <button 
              className="close-btn"
              onClick={() => setShowPreview(false)}
            >
              ×
            </button>
          </div>
          
          <div className="modal-body">
            <div className="quiz-info">
              <p><strong>Subject:</strong> {currentQuiz.subject}</p>
              <p><strong>Topic:</strong> {currentQuiz.topic}</p>
              <p><strong>Difficulty:</strong> {currentQuiz.difficulty}</p>
              <p><strong>Questions:</strong> {currentQuiz.questions?.length || 0}</p>
            </div>

            <div className="questions-list">
              {currentQuiz.questions?.map((question, index) => (
                <div key={index} className="question-preview">
                  <div className="question-header">
                    <h4>Question {index + 1}</h4>
                    <button 
                      className="edit-btn"
                      onClick={() => handleEditQuestion(question, index)}
                    >
                      ✏️ Edit
                    </button>
                  </div>
                  
                  <p className="question-text">{question.question}</p>
                  
                  <div className="options-list">
                    {question.options?.map((option, optIndex) => (
                      <div 
                        key={optIndex} 
                        className={`option ${option === question.correct_answer ? 'correct' : ''}`}
                      >
                        <span className="option-letter">{String.fromCharCode(65 + optIndex)}</span>
                        <span className="option-text">{option}</span>
                        {option === question.correct_answer && <span className="correct-mark">✓</span>}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="modal-footer">
            <div className="download-actions">
              <button 
                onClick={() => handleDownload(currentQuiz.id, 'pdf')}
                className="download-btn pdf"
                disabled={loading}
              >
                📄 Download PDF
              </button>
              <button 
                onClick={() => handleDownload(currentQuiz.id, 'word')}
                className="download-btn word"
                disabled={loading}
              >
                📝 Download Word
              </button>
              <button 
                onClick={() => handleDownload(currentQuiz.id, 'excel')}
                className="download-btn excel"
                disabled={loading}
              >
                📊 Download Excel
              </button>
            </div>
            <button 
              className="close-modal-btn"
              onClick={() => setShowPreview(false)}
            >
              Close Preview
            </button>
          </div>
        </div>
      </div>
    );
  };

  const QuestionEditModal = () => {
    if (!editingQuestion) return null;

    const [editForm, setEditForm] = useState({
      question: editingQuestion.question,
      options: [...editingQuestion.options],
      correct_answer: editingQuestion.correct_answer
    });

    const handleEditFormChange = (field, value, index = null) => {
      if (field === 'option') {
        const newOptions = [...editForm.options];
        newOptions[index] = value;
        setEditForm({ ...editForm, options: newOptions });
      } else {
        setEditForm({ ...editForm, [field]: value });
      }
    };

    const saveQuestion = () => {
      handleSaveQuestion({
        ...editForm,
        index: editingQuestion.index
      });
    };

    return (
      <div className="modal-overlay" onClick={() => setEditingQuestion(null)}>
        <div className="modal-content" onClick={e => e.stopPropagation()}>
          <div className="modal-header">
            <h2>✏️ Edit Question {editingQuestion.index + 1}</h2>
            <button 
              className="close-btn"
              onClick={() => setEditingQuestion(null)}
            >
              ×
            </button>
          </div>
          
          <div className="modal-body">
            <div className="form-group">
              <label>Question:</label>
              <textarea
                value={editForm.question}
                onChange={(e) => handleEditFormChange('question', e.target.value)}
                className="form-input"
                rows="3"
              />
            </div>

            <div className="options-edit">
              <label>Options:</label>
              {editForm.options.map((option, index) => (
                <div key={index} className="option-edit">
                  <span className="option-label">{String.fromCharCode(65 + index)})</span>
                  <input
                    type="text"
                    value={option}
                    onChange={(e) => handleEditFormChange('option', e.target.value, index)}
                    className="form-input"
                  />
                  <input
                    type="radio"
                    name="correct"
                    checked={option === editForm.correct_answer}
                    onChange={() => handleEditFormChange('correct_answer', option)}
                  />
                  <span>Correct</span>
                </div>
              ))}
            </div>
          </div>

          <div className="modal-footer">
            <button className="save-btn" onClick={saveQuestion}>
              💾 Save Changes
            </button>
            <button 
              className="cancel-btn" 
              onClick={() => setEditingQuestion(null)}
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div className="header-content">
          <div className="dashboard-title">
            <span className="welcome">Welcome back, {user?.name || 'User'}!</span>
            <span className="user-role">{user?.role || 'Guest'}</span>
          </div>
          <div className="header-actions">
            <span className="role-badge">{user?.role}</span>
            <button onClick={onLogout} className="logout-btn">
              🚪 Logout
            </button>
          </div>
        </div>
      </div>

      <div className="dashboard-main">
        <div className="dashboard-content">
          {user?.role === 'lecturer' ? (
            <>
              <div className="dashboard-tabs">
                <button
                  className={`tab-btn ${activeTab === 'create' ? 'active' : ''}`}
                  onClick={() => setActiveTab('create')}
                >
                  <span className="tab-icon">✨</span>
                  Create Quiz
                </button>
                <button
                  className={`tab-btn ${activeTab === 'manage' ? 'active' : ''}`}
                  onClick={() => setActiveTab('manage')}
                >
                  <span className="tab-icon">📚</span>
                  My Quizzes ({quizzes.length})
                </button>
                <button
                  className={`tab-btn ${activeTab === 'analytics' ? 'active' : ''}`}
                  onClick={() => setActiveTab('analytics')}
                >
                  <span className="tab-icon">📊</span>
                  Analytics
                </button>
              </div>

              <div className="tab-content">
                {activeTab === 'create' && (
                  <div className="create-quiz-section">
                    <h2>✨ Create New Quiz</h2>
                    
                    {error && (
                      <div className="error-message">
                        ⚠️ {error}
                      </div>
                    )}

                    <form onSubmit={handleCreateQuiz} className="create-quiz-form">
                      <div className="form-grid">
                        <div className="form-group">
                          <label>📝 Quiz Title</label>
                          <input
                            type="text"
                            name="title"
                            value={formData.title}
                            onChange={handleInputChange}
                            placeholder="Enter quiz title..."
                            required
                            className="form-input"
                          />
                        </div>

                        <div className="form-group">
                          <label>📚 Subject</label>
                          <input
                            type="text"
                            name="subject"
                            value={formData.subject}
                            onChange={handleInputChange}
                            placeholder="e.g., Mathematics, Science..."
                            required
                            className="form-input"
                          />
                        </div>

                        <div className="form-group">
                          <label>🎯 Topic</label>
                          <input
                            type="text"
                            name="topic"
                            value={formData.topic}
                            onChange={handleInputChange}
                            placeholder="Specific topic to focus on..."
                            required
                            className="form-input"
                          />
                        </div>

                        <div className="form-group">
                          <label>⚡ Difficulty Level</label>
                          <select
                            name="difficulty"
                            value={formData.difficulty}
                            onChange={handleInputChange}
                            className="form-input"
                          >
                            <option value="easy">🟢 Easy</option>
                            <option value="medium">🟡 Medium</option>
                            <option value="hard">🔴 Hard</option>
                          </select>
                        </div>

                        <div className="form-group">
                          <label>📊 Number of Questions</label>
                          <select
                            name="questionCount"
                            value={formData.questionCount}
                            onChange={handleInputChange}
                            className="form-input"
                          >
                            <option value="5">5 Questions</option>
                            <option value="10">10 Questions</option>
                            <option value="15">15 Questions</option>
                            <option value="20">20 Questions</option>
                            <option value="25">25 Questions</option>
                          </select>
                        </div>
                      </div>

                      <button 
                        type="submit" 
                        className="create-btn"
                        disabled={loading}
                      >
                        {loading ? (
                          <>
                            <span className="loading-spinner"></span>
                            Generating Quiz...
                          </>
                        ) : (
                          <>
                            🚀 Generate Quiz Preview
                          </>
                        )}
                      </button>
                    </form>
                  </div>
                )}

                {activeTab === 'manage' && (
                  <div className="manage-quiz-section">
                    <div className="section-header">
                      <h2>📚 My Quizzes</h2>
                      <div className="quiz-stats">
                        <div className="stat-card">
                          <span className="stat-number">{quizzes.length}</span>
                          <span className="stat-label">Total Quizzes</span>
                        </div>
                      </div>
                    </div>

                    {quizzes.length === 0 ? (
                      <div className="empty-state">
                        <div className="empty-icon">📝</div>
                        <h3>No quizzes created yet</h3>
                        <p>Create your first quiz to get started!</p>
                        <button 
                          onClick={() => setActiveTab('create')}
                          className="action-btn"
                        >
                          ✨ Create Your First Quiz
                        </button>
                      </div>
                    ) : (
                      <div className="quizzes-grid">
                        {quizzes.map((quiz) => (
                          <div key={quiz.id} className="quiz-card">
                            <div className="quiz-header">
                              <h3>{quiz.title}</h3>
                              <span className="quiz-date">
                                {new Date(quiz.created_at).toLocaleDateString()}
                              </span>
                            </div>
                            
                            <div className="quiz-details">
                              <span className="detail">📚 {quiz.subject}</span>
                              <span className="detail">🎯 {quiz.topic}</span>
                              <span className="detail">⚡ {quiz.difficulty}</span>
                              <span className="detail">📊 {quiz.questions?.length || 0} Questions</span>
                            </div>

                            <div className="quiz-actions">
                              <button 
                                onClick={() => {
                                  setCurrentQuiz(quiz);
                                  setShowPreview(true);
                                }}
                                className="preview-btn"
                              >
                                👁️ Preview
                              </button>
                              <button 
                                onClick={() => handleDownload(quiz.id, 'pdf')}
                                className="download-btn pdf"
                                disabled={loading}
                              >
                                📄 PDF
                              </button>
                              <button 
                                onClick={() => handleDownload(quiz.id, 'word')}
                                className="download-btn word"
                                disabled={loading}
                              >
                                📝 Word
                              </button>
                              <button 
                                onClick={() => handleDownload(quiz.id, 'excel')}
                                className="download-btn excel"
                                disabled={loading}
                              >
                                📊 Excel
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {activeTab === 'analytics' && (
                  <div className="analytics-section">
                    <h2>📊 Quiz Analytics</h2>
                    <div className="coming-soon">
                      <div className="coming-soon-icon">📈</div>
                      <h3>Analytics Dashboard Coming Soon</h3>
                      <p>Track student performance, quiz completion rates, and detailed insights!</p>
                      <div className="feature-list">
                        <div className="feature">✅ Student Performance Tracking</div>
                        <div className="feature">✅ Quiz Completion Analytics</div>
                        <div className="feature">✅ Difficulty Analysis</div>
                        <div className="feature">✅ Subject Performance Metrics</div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </>
          ) : (
            // Student Dashboard
            <div className="student-dashboard">
              <h2>🎓 Student Portal</h2>
              <div className="coming-soon">
                <div className="coming-soon-icon">📚</div>
                <h3>Student Quiz Interface Coming Soon</h3>
                <p>Take quizzes, view scores, and track your progress!</p>
                <div className="feature-list">
                  <div className="feature">✅ Interactive Quiz Taking</div>
                  <div className="feature">✅ Real-time Scoring</div>
                  <div className="feature">✅ Progress Tracking</div>
                  <div className="feature">✅ Performance Analytics</div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Modals */}
      <QuizPreview />
      <QuestionEditModal />

      {/* Loading Overlay */}
      {loading && (
        <div className="loading-overlay">
          <div className="loading-spinner-large"></div>
          <p>Processing...</p>
        </div>
      )}
    </div>
  );
};

export default Dashboard;