import React, { useState, useEffect } from 'react';
import './Dashboard.css';

const Dashboard = ({ user, onLogout, onStartQuiz }) => {
  const [activeTab, setActiveTab] = useState(user.role === 'lecturer' ? 'create' : 'available');
  const [quizzes, setQuizzes] = useState([]);
  const [students, setStudents] = useState([]);
  const [grades, setGrades] = useState([]);
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (user.role === 'lecturer') {
      fetchQuizzes();
      fetchStudents();
      fetchGrades();
    } else {
      fetchStudentQuizzes();
    }
  }, [user.role]);

  const showMessage = (msg) => {
    setMessage(msg);
    setTimeout(() => setMessage(''), 3000);
  };

  const fetchQuizzes = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/api/lecturer/quizzes', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const data = await response.json();
      setQuizzes(data.quizzes || []);
    } catch (error) {
      console.error('Error fetching quizzes:', error);
      showMessage('Failed to load quizzes');
    }
  };

  const fetchStudents = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/api/lecturer/students', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const data = await response.json();
      setStudents(data.students || []);
    } catch (error) {
      console.error('Error fetching students:', error);
      showMessage('Failed to load students');
    }
  };

  const fetchGrades = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/api/lecturer/grades', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const data = await response.json();
      setGrades(data.grades || []);
    } catch (error) {
      console.error('Error fetching grades:', error);
      showMessage('Failed to load grades');
    }
  };

  const fetchStudentQuizzes = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/api/student/quizzes', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const data = await response.json();
      setQuizzes(data.quizzes || []);
    } catch (error) {
      console.error('Error fetching student quizzes:', error);
      showMessage('Failed to load available quizzes');
    }
  };

  const downloadQuiz = async (quizId, format = 'pdf') => {
    try {
      showMessage(`Downloading quiz in ${format.toUpperCase()} format...`);
      const response = await fetch(`http://127.0.0.1:5000/api/quiz/${quizId}/download?format=${format}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `quiz_${quizId}.${format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        showMessage(`Quiz downloaded successfully as ${format.toUpperCase()}!`);
      } else {
        showMessage('Download failed. Please try again.');
      }
    } catch (error) {
      console.error('Error downloading quiz:', error);
      showMessage('Failed to download quiz. Please try again.');
    }
  };

  const downloadGrades = async (format = 'csv') => {
    try {
      showMessage(`Downloading grades in ${format.toUpperCase()} format...`);
      const response = await fetch(`http://127.0.0.1:5000/api/lecturer/grades/download?format=${format}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `grades.${format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        showMessage(`Grades downloaded successfully as ${format.toUpperCase()}!`);
      } else {
        showMessage('Download failed. Please try again.');
      }
    } catch (error) {
      console.error('Error downloading grades:', error);
      showMessage('Failed to download grades. Please try again.');
    }
  };

  const handleStartQuiz = (quiz) => {
    showMessage(`Starting ${quiz.topic} quiz...`);
    if (onStartQuiz) {
      onStartQuiz();
    }
  };

  const handleViewDetails = (item) => {
    showMessage(`Viewing details for ${item.topic || item.user_name || 'item'}`);
  };

  const handleShareQuiz = (quiz) => {
    const shareUrl = `${window.location.origin}/quiz/${quiz.id}`;
    if (navigator.clipboard) {
      navigator.clipboard.writeText(shareUrl);
      showMessage('Quiz link copied to clipboard!');
    } else {
      showMessage(`Share this link: ${shareUrl}`);
    }
  };

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-content">
          <h1 className="dashboard-title">
            <span className="welcome">Welcome back,</span>
            <span className="user-name">{user.name}</span>
          </h1>
          <div className="header-actions">
            <div className="user-role">
              <span className={`role-badge ${user.role}`}>
                {user.role === 'lecturer' ? '👨‍🏫 Lecturer' : '👨‍🎓 Student'}
              </span>
            </div>
            <button className="logout-btn" onClick={onLogout}>
              <span>🚪</span>
              Logout
            </button>
          </div>
        </div>
      </header>

      {message && (
        <div className="message-banner">
          {message}
        </div>
      )}

      <main className="dashboard-main">
        {user.role === 'lecturer' ? renderLecturerDashboard() : renderStudentDashboard()}
      </main>
    </div>
  );

  function renderLecturerDashboard() {
    return (
      <div className="dashboard-content">
        <div className="dashboard-tabs">
          <button 
            className={`tab-btn ${activeTab === 'create' ? 'active' : ''}`}
            onClick={() => setActiveTab('create')}
          >
            <span className="tab-icon">➕</span>
            Create Quiz
          </button>
          <button 
            className={`tab-btn ${activeTab === 'quizzes' ? 'active' : ''}`}
            onClick={() => setActiveTab('quizzes')}
          >
            <span className="tab-icon">📚</span>
            My Quizzes
          </button>
          <button 
            className={`tab-btn ${activeTab === 'students' ? 'active' : ''}`}
            onClick={() => setActiveTab('students')}
          >
            <span className="tab-icon">👥</span>
            Students
          </button>
          <button 
            className={`tab-btn ${activeTab === 'grades' ? 'active' : ''}`}
            onClick={() => setActiveTab('grades')}
          >
            <span className="tab-icon">📊</span>
            Grades
          </button>
        </div>

        <div className="tab-content">
          {activeTab === 'create' && <CreateQuizTab onQuizCreated={fetchQuizzes} showMessage={showMessage} />}
          {activeTab === 'quizzes' && <QuizzesTab quizzes={quizzes} onDownload={downloadQuiz} onShare={handleShareQuiz} />}
          {activeTab === 'students' && <StudentsTab students={students} />}
          {activeTab === 'grades' && <GradesTab grades={grades} onDownload={downloadGrades} onView={handleViewDetails} />}
        </div>
      </div>
    );
  }

  function renderStudentDashboard() {
    return (
      <div className="dashboard-content">
        <div className="dashboard-tabs">
          <button 
            className={`tab-btn ${activeTab === 'available' ? 'active' : ''}`}
            onClick={() => setActiveTab('available')}
          >
            <span className="tab-icon">📋</span>
            Available Quizzes
          </button>
          <button 
            className={`tab-btn ${activeTab === 'take' ? 'active' : ''}`}
            onClick={() => setActiveTab('take')}
          >
            <span className="tab-icon">✏️</span>
            Take Quiz
          </button>
          <button 
            className={`tab-btn ${activeTab === 'completed' ? 'active' : ''}`}
            onClick={() => setActiveTab('completed')}
          >
            <span className="tab-icon">✅</span>
            Completed
          </button>
          <button 
            className={`tab-btn ${activeTab === 'results' ? 'active' : ''}`}
            onClick={() => setActiveTab('results')}
          >
            <span className="tab-icon">📈</span>
            My Results
          </button>
        </div>

        <div className="tab-content">
          {activeTab === 'available' && <AvailableQuizzesTab quizzes={quizzes} onStartQuiz={handleStartQuiz} />}
          {activeTab === 'take' && <TakeQuizTab onStartQuiz={onStartQuiz} />}
          {activeTab === 'completed' && <CompletedQuizzesTab grades={grades} onView={handleViewDetails} />}
          {activeTab === 'results' && <StudentResultsTab grades={grades} onView={handleViewDetails} onRetake={handleStartQuiz} />}
        </div>
      </div>
    );
  }
};

// Create Quiz Tab Component
const CreateQuizTab = ({ onQuizCreated, showMessage }) => {
  const [formData, setFormData] = useState({
    topic: '',
    numQuestions: 5,
    difficulty: 'medium',
    timeLimit: 30
  });
  const [loading, setLoading] = useState(false);

  const handleCreateQuiz = async (e) => {
    e.preventDefault();
    
    if (!formData.topic.trim()) {
      showMessage('Please enter a topic for the quiz');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('http://127.0.0.1:5000/api/quiz', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          topic: formData.topic,
          num_questions: formData.numQuestions,
          difficulty: formData.difficulty,
          time_limit: formData.timeLimit
        })
      });

      if (response.ok) {
        const data = await response.json();
        showMessage(`✅ Quiz "${formData.topic}" created successfully with ${data.questions.length} questions!`);
        setFormData({ topic: '', numQuestions: 5, difficulty: 'medium', timeLimit: 30 });
        if (onQuizCreated) onQuizCreated();
      } else {
        const error = await response.json();
        showMessage(`❌ Failed to create quiz: ${error.error || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error creating quiz:', error);
      showMessage('❌ Failed to create quiz. Please check your connection and try again.');
    }
    setLoading(false);
  };

  return (
    <div className="create-quiz-section">
      <h2>Create New Quiz</h2>
      <form onSubmit={handleCreateQuiz} className="create-quiz-form">
        <div className="form-grid">
          <div className="form-group">
            <label>Topic</label>
            <input
              type="text"
              value={formData.topic}
              onChange={(e) => setFormData({...formData, topic: e.target.value})}
              placeholder="Enter quiz topic (e.g., JavaScript, Math, History)"
              required
            />
          </div>
          <div className="form-group">
            <label>Number of Questions</label>
            <select
              value={formData.numQuestions}
              onChange={(e) => setFormData({...formData, numQuestions: parseInt(e.target.value)})}
            >
              {[5, 10, 15, 20].map(num => (
                <option key={num} value={num}>{num} Questions</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>Difficulty</label>
            <select
              value={formData.difficulty}
              onChange={(e) => setFormData({...formData, difficulty: e.target.value})}
            >
              <option value="easy">🟢 Easy</option>
              <option value="medium">🟡 Medium</option>
              <option value="hard">🔴 Hard</option>
            </select>
          </div>
          <div className="form-group">
            <label>Time Limit (minutes)</label>
            <input
              type="number"
              value={formData.timeLimit}
              onChange={(e) => setFormData({...formData, timeLimit: parseInt(e.target.value)})}
              min="5"
              max="120"
            />
          </div>
        </div>
        <button type="submit" className="create-btn" disabled={loading}>
          {loading ? (
            <>
              <div className="loading-spinner-small"></div>
              Creating Quiz...
            </>
          ) : (
            <>
              <span>✨</span>
              Generate Quiz
            </>
          )}
        </button>
      </form>
    </div>
  );
};

// Quizzes Tab Component
const QuizzesTab = ({ quizzes, onDownload, onShare }) => (
  <div className="quizzes-section">
    <div className="section-header">
      <h2>My Quizzes</h2>
      <div className="quiz-stats">
        <div className="stat-card">
          <span className="stat-number">{quizzes.length}</span>
          <span className="stat-label">Total Quizzes</span>
        </div>
      </div>
    </div>
    <div className="quizzes-grid">
      {quizzes.length > 0 ? quizzes.map((quiz, index) => (
        <div key={index} className="quiz-card">
          <div className="quiz-header">
            <h3>{quiz.topic || `Quiz ${index + 1}`}</h3>
            <span className="quiz-date">{new Date(quiz.created_at).toLocaleDateString()}</span>
          </div>
          <div className="quiz-details">
            <span>📝 {quiz.num_questions} Questions</span>
            <span>🎯 {quiz.difficulty}</span>
          </div>
          <div className="quiz-actions">
            <button 
              className="download-btn pdf"
              onClick={() => onDownload(quiz.id, 'pdf')}
            >
              📄 PDF
            </button>
            <button 
              className="download-btn word"
              onClick={() => onDownload(quiz.id, 'docx')}
            >
              📘 Word
            </button>
            <button 
              className="share-btn"
              onClick={() => onShare(quiz)}
            >
              🔗 Share
            </button>
          </div>
        </div>
      )) : (
        <div className="empty-state">
          <p>No quizzes created yet. Start by creating your first quiz!</p>
        </div>
      )}
    </div>
  </div>
);

// Students Tab Component
const StudentsTab = ({ students }) => (
  <div className="students-section">
    <h2>Registered Students</h2>
    <div className="students-grid">
      {students.length > 0 ? students.map((student, index) => (
        <div key={index} className="student-card">
          <div className="student-avatar">
            {student.name ? student.name.charAt(0) : 'S'}
          </div>
          <div className="student-info">
            <h3>{student.name || `Student ${index + 1}`}</h3>
            <p>{student.email || 'student@example.com'}</p>
            <div className="student-stats">
              <span>📅 Joined: {new Date(student.created_at).toLocaleDateString()}</span>
            </div>
          </div>
        </div>
      )) : (
        <div className="empty-state">
          <p>No students registered yet.</p>
        </div>
      )}
    </div>
  </div>
);

// Grades Tab Component
const GradesTab = ({ grades, onDownload, onView }) => (
  <div className="grades-section">
    <div className="section-header">
      <h2>Student Grades</h2>
      <div className="download-actions">
        <button 
          className="download-btn excel"
          onClick={() => onDownload('excel')}
        >
          📊 Excel
        </button>
        <button 
          className="download-btn csv"
          onClick={() => onDownload('csv')}
        >
          📋 CSV
        </button>
      </div>
    </div>
    <div className="grades-table">
      <table>
        <thead>
          <tr>
            <th>Student</th>
            <th>Email</th>
            <th>Topic</th>
            <th>Score</th>
            <th>Percentage</th>
            <th>Date</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {grades.length > 0 ? (
            grades.map((grade, index) => (
              <tr key={index}>
                <td>{grade.user_name || `Student ${index + 1}`}</td>
                <td>{grade.user_email || 'student@example.com'}</td>
                <td>{grade.topic || 'Sample Quiz'}</td>
                <td>{grade.score || 0}/{grade.total || 10}</td>
                <td>
                  <span className={`score-badge ${
                    (grade.percentage || 0) >= 90 ? 'excellent' : 
                    (grade.percentage || 0) >= 75 ? 'good' : 'needs-improvement'
                  }`}>
                    {grade.percentage || 0}%
                  </span>
                </td>
                <td>{grade.completed_at ? new Date(grade.completed_at).toLocaleDateString() : 'Today'}</td>
                <td>
                  <button 
                    className="view-btn"
                    onClick={() => onView(grade)}
                  >
                    👁️ View
                  </button>
                </td>
              </tr>
            ))
          ) : (
            // Show sample data when no grades available
            [
              { id: 1, user_name: 'John Doe', user_email: 'john@example.com', topic: 'Mathematics', score: 8, total: 10, percentage: 85, completed_at: new Date().toISOString() },
              { id: 2, user_name: 'Jane Smith', user_email: 'jane@example.com', topic: 'Science', score: 9, total: 10, percentage: 92, completed_at: new Date().toISOString() }
            ].map((grade, index) => (
              <tr key={index}>
                <td>{grade.user_name}</td>
                <td>{grade.user_email}</td>
                <td>{grade.topic}</td>
                <td>{grade.score}/{grade.total}</td>
                <td>
                  <span className={`score-badge ${
                    grade.percentage >= 90 ? 'excellent' : 
                    grade.percentage >= 75 ? 'good' : 'needs-improvement'
                  }`}>
                    {grade.percentage}%
                  </span>
                </td>
                <td>{new Date(grade.completed_at).toLocaleDateString()}</td>
                <td>
                  <button 
                    className="view-btn"
                    onClick={() => onView(grade)}
                  >
                    👁️ View
                  </button>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  </div>
);

// Student components
const AvailableQuizzesTab = ({ quizzes, onStartQuiz }) => (
  <div className="available-quizzes">
    <h2>Available Quizzes</h2>
    <div className="quiz-list">
      {quizzes.length > 0 ? (
        quizzes.map((quiz, index) => (
          <div key={index} className="quiz-item">
            <h3>{quiz.topic || `Quiz ${index + 1}`}</h3>
            <p>📝 {quiz.num_questions || 5} questions • 🎯 {quiz.difficulty || 'Medium'}</p>
            <p>👨‍🏫 Created by: {quiz.created_by_name || 'Instructor'}</p>
            <button 
              className="start-quiz-btn"
              onClick={() => onStartQuiz(quiz)}
            >
              🚀 Start Quiz
            </button>
          </div>
        ))
      ) : (
        <div className="empty-state">
          <p>No quizzes available at the moment. Check back later!</p>
        </div>
      )}
    </div>
  </div>
);

const TakeQuizTab = ({ onStartQuiz }) => (
  <div className="take-quiz-section">
    <h2>🎯 Take a Quiz</h2>
    <div className="custom-quiz-card">
      <h3>Create Custom Quiz</h3>
      <p>Generate a personalized quiz on any topic you want to learn!</p>
      <button 
        className="custom-quiz-btn"
        onClick={onStartQuiz}
      >
        🎨 Create Custom Quiz
      </button>
    </div>
  </div>
);

const CompletedQuizzesTab = ({ grades, onView }) => (
  <div className="completed-quizzes">
    <h2>Completed Quizzes</h2>
    <div className="quiz-list">
      {grades.length > 0 ? (
        grades.map((grade, index) => (
          <div key={index} className="quiz-item completed">
            <h3>{grade.topic} Quiz</h3>
            <p>Score: {grade.score}/{grade.total} ({grade.percentage}%)</p>
            <div className="quiz-meta">
              <span className="completed-date">Completed: {new Date(grade.completed_at).toLocaleDateString()}</span>
            </div>
            <button 
              className="view-btn"
              onClick={() => onView(grade)}
            >
              📄 View Details
            </button>
          </div>
        ))
      ) : (
        <div className="empty-state">
          <p>No completed quizzes yet. Start taking some quizzes!</p>
        </div>
      )}
    </div>
  </div>
);

const StudentResultsTab = ({ grades, onView, onRetake }) => (
  <div className="student-results">
    <h2>My Results & Statistics</h2>
    
    {/* Statistics Cards */}
    <div className="stats-grid">
      <div className="stat-card">
        <div className="stat-icon">📊</div>
        <div className="stat-number">{grades.length}</div>
        <div className="stat-label">Total Quizzes</div>
      </div>
      <div className="stat-card">
        <div className="stat-icon">⭐</div>
        <div className="stat-number">
          {grades.length > 0 ? Math.round(grades.reduce((sum, grade) => sum + grade.percentage, 0) / grades.length) : 0}%
        </div>
        <div className="stat-label">Average Score</div>
      </div>
      <div className="stat-card">
        <div className="stat-icon">🏆</div>
        <div className="stat-number">
          {grades.length > 0 ? Math.max(...grades.map(g => g.percentage)) : 0}%
        </div>
        <div className="stat-label">Best Score</div>
      </div>
    </div>

    {/* Results Table */}
    <div className="results-table">
      <h3>Subject Performance</h3>
      <table>
        <thead>
          <tr>
            <th>Subject</th>
            <th>Best Score</th>
            <th>Date</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {grades.length > 0 ? grades.map((result, index) => (
            <tr key={index}>
              <td>{result.topic}</td>
              <td>
                <span className={`score-badge ${result.percentage >= 90 ? 'excellent' : result.percentage >= 75 ? 'good' : 'needs-improvement'}`}>
                  {result.percentage}%
                </span>
              </td>
              <td>{new Date(result.completed_at).toLocaleDateString()}</td>
              <td>
                <button 
                  className="action-btn view"
                  onClick={() => onView(result)}
                >
                  📄 View
                </button>
                <button 
                  className="action-btn retake"
                  onClick={() => onRetake(result)}
                >
                  🔄 Retake
                </button>
              </td>
            </tr>
          )) : (
            <tr>
              <td colSpan="4">No results yet. Take some quizzes to see your performance!</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  </div>
);

export default Dashboard;
