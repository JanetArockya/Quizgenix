import React, { useState, useEffect } from 'react';
import './Dashboard.css';

const Dashboard = ({ user, onLogout, onStartQuiz }) => {
  const [activeTab, setActiveTab] = useState('create');
  const [quizzes, setQuizzes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPreview, setShowPreview] = useState(false);
  const [currentQuiz, setCurrentQuiz] = useState(null);
  const [editingQuestion, setEditingQuestion] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    subject: '',
    topic: '',
    difficulty: 'medium',
    questionCount: 10
  });

  // Fetch quizzes on component mount
  useEffect(() => {
    if (user.role === 'lecturer') {
      fetchQuizzes();
    }
  }, [user.role]);

  const fetchQuizzes = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://127.0.0.1:5000/api/quizzes', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setQuizzes(data.quizzes || []);
      }
    } catch (error) {
      console.error('Error fetching quizzes:', error);
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
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (response.ok) {
        setCurrentQuiz(data);
        setShowPreview(true);
        setFormData({
          title: '',
          subject: '',
          topic: '',
          difficulty: 'medium',
          questionCount: 10
        });
      } else {
        setError(data.error || 'Failed to create quiz');
      }
    } catch (error) {
      setError('Network error. Please try again.');
    }

    setLoading(false);
  };

  const handleSaveQuiz = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      const response = await fetch(`http://127.0.0.1:5000/api/quiz/${currentQuiz.id}/save`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(currentQuiz),
      });

      if (response.ok) {
        setShowPreview(false);
        setCurrentQuiz(null);
        fetchQuizzes();
        alert('Quiz saved successfully!');
      } else {
        const data = await response.json();
        setError(data.error || 'Failed to save quiz');
      }
    } catch (error) {
      setError('Failed to save quiz. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleEditQuestion = (questionIndex) => {
    setEditingQuestion({
      index: questionIndex,
      ...currentQuiz.questions[questionIndex]
    });
  };

  const handleUpdateQuestion = () => {
    const updatedQuestions = [...currentQuiz.questions];
    updatedQuestions[editingQuestion.index] = {
      question: editingQuestion.question,
      options: editingQuestion.options,
      correct_answer: editingQuestion.correct_answer
    };
    
    setCurrentQuiz({
      ...currentQuiz,
      questions: updatedQuestions
    });
    
    setEditingQuestion(null);
  };

  const handleDeleteQuestion = (questionIndex) => {
    if (window.confirm('Are you sure you want to delete this question?')) {
      const updatedQuestions = currentQuiz.questions.filter((_, index) => index !== questionIndex);
      setCurrentQuiz({
        ...currentQuiz,
        questions: updatedQuestions
      });
    }
  };

  const handleDownload = async (quizId, fileType) => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      const response = await fetch(`http://127.0.0.1:5000/api/quiz/${quizId}/download/${fileType}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const contentDisposition = response.headers.get('content-disposition');
        let filename = `quiz_${quizId}.${fileType === 'word' ? 'docx' : fileType === 'excel' ? 'xlsx' : 'pdf'}`;
        
        if (contentDisposition) {
          const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
          if (filenameMatch) {
            filename = filenameMatch[1];
          }
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        setError('');
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Download failed');
      }
    } catch (error) {
      console.error('Download error:', error);
      setError('Failed to download file. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Quiz Preview Modal Component
  const QuizPreview = () => {
    if (!showPreview || !currentQuiz) return null;

    return (
      <div className="quiz-preview-overlay">
        <div className="quiz-preview-modal">
          <div className="preview-header">
            <h2>📋 Quiz Preview: {currentQuiz.title}</h2>
            <div className="preview-actions">
              <button onClick={handleSaveQuiz} className="save-btn" disabled={loading}>
                💾 Save Quiz
              </button>
              <button onClick={() => setShowPreview(false)} className="close-btn">
                ✖️ Close
              </button>
            </div>
          </div>
          
          <div className="preview-content">
            <div className="quiz-info-bar">
              <span>📚 Subject: {currentQuiz.subject}</span>
              <span>🎯 Difficulty: {currentQuiz.difficulty}</span>
              <span>📊 Questions: {currentQuiz.questions?.length || 0}</span>
            </div>

            <div className="questions-preview">
              {currentQuiz.questions?.map((question, index) => (
                <div key={index} className="question-preview-card">
                  <div className="question-header">
                    <h3>Question {index + 1}</h3>
                    <div className="question-actions">
                      <button 
                        onClick={() => handleEditQuestion(index)}
                        className="edit-btn"
                      >
                        ✏️ Edit
                      </button>
                      <button 
                        onClick={() => handleDeleteQuestion(index)}
                        className="delete-btn"
                      >
                        🗑️ Delete
                      </button>
                    </div>
                  </div>
                  
                  <p className="question-text">{question.question}</p>
                  
                  <div className="options-list">
                    {question.options?.map((option, optIndex) => (
                      <div 
                        key={optIndex} 
                        className={`option-item ${option === question.correct_answer ? 'correct' : ''}`}
                      >
                        <span className="option-letter">{String.fromCharCode(65 + optIndex)}</span>
                        <span className="option-text">{option}</span>
                        {option === question.correct_answer && <span className="correct-badge">✅</span>}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Question Edit Modal Component
  const QuestionEditModal = () => {
    if (!editingQuestion) return null;

    return (
      <div className="edit-modal-overlay">
        <div className="edit-modal">
          <div className="edit-modal-header">
            <h3>✏️ Edit Question {editingQuestion.index + 1}</h3>
            <button onClick={() => setEditingQuestion(null)} className="close-btn">✖️</button>
          </div>
          
          <div className="edit-modal-content">
            <div className="form-group">
              <label>Question:</label>
              <textarea
                value={editingQuestion.question}
                onChange={(e) => setEditingQuestion({
                  ...editingQuestion,
                  question: e.target.value
                })}
                className="question-textarea"
                rows="3"
              />
            </div>

            <div className="options-edit">
              <label>Options:</label>
              {editingQuestion.options?.map((option, index) => (
                <div key={index} className="option-edit-group">
                  <span className="option-label">{String.fromCharCode(65 + index)})</span>
                  <input
                    type="text"
                    value={option}
                    onChange={(e) => {
                      const newOptions = [...editingQuestion.options];
                      newOptions[index] = e.target.value;
                      setEditingQuestion({
                        ...editingQuestion,
                        options: newOptions
                      });
                    }}
                    className="option-input"
                  />
                  <input
                    type="radio"
                    name="correctAnswer"
                    checked={option === editingQuestion.correct_answer}
                    onChange={() => setEditingQuestion({
                      ...editingQuestion,
                      correct_answer: option
                    })}
                    className="correct-radio"
                  />
                  <label className="radio-label">Correct</label>
                </div>
              ))}
            </div>

            <div className="edit-actions">
              <button onClick={handleUpdateQuestion} className="update-btn">
                ✅ Update Question
              </button>
              <button onClick={() => setEditingQuestion(null)} className="cancel-btn">
                ❌ Cancel
              </button>
            </div>
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
            <span className="welcome">Welcome back!</span>
            <span className="user-name">{user.name}</span>
          </div>
          <div className="header-actions">
            <span className="role-badge">{user.role}</span>
            <button onClick={onLogout} className="logout-btn">
              Logout
            </button>
          </div>
        </div>
      </div>

      <div className="dashboard-main">
        <div className="dashboard-content">
          {user.role === 'lecturer' ? (
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
                  My Quizzes
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
                    <h2>Create New Quiz</h2>
                    
                    {error && (
                      <div className="error-message">
                        {error}
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
                            <span className="loading-spinner-small"></span>
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
                      <h2>My Quizzes</h2>
                      <div className="quiz-stats">
                        <div className="stat-card">
                          <span className="stat-number">{quizzes.length}</span>
                          <span className="stat-label">Total Quizzes</span>
                        </div>
                      </div>
                    </div>

                    {quizzes.length === 0 ? (
                      <div className="empty-state">
                        <p>📝 No quizzes created yet</p>
                        <button 
                          onClick={() => setActiveTab('create')}
                          className="action-btn"
                        >
                          Create Your First Quiz
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
                              <span>📚 {quiz.subject}</span>
                              <span>🎯 {quiz.difficulty}</span>
                              <span>📊 {quiz.questions?.length || 0} Questions</span>
                            </div>

                            <div className="quiz-actions">
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
                              <button 
                                onClick={() => {
                                  setCurrentQuiz(quiz);
                                  setShowPreview(true);
                                }}
                                className="edit-quiz-btn"
                              >
                                ✏️ Edit
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
                      <p>📈 Analytics dashboard coming soon...</p>
                      <p>Track student performance, quiz completion rates, and more!</p>
                    </div>
                  </div>
                )}
              </div>
            </>
          ) : (
            // Student Dashboard
            <div className="student-dashboard">
              <h2>🎓 Available Quizzes</h2>
              <div className="coming-soon">
                <p>📚 Student quiz interface coming soon...</p>
                <p>Take quizzes, view scores, and track your progress!</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Modals */}
      <QuizPreview />
      <QuestionEditModal />
    </div>
  );
};

export default Dashboard;