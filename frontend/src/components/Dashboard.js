import React, { useState, useEffect } from 'react';
import './Dashboard.css';

const Dashboard = ({ user, onLogout, onStartQuiz }) => {
  const [activeTab, setActiveTab] = useState('create');
  const [quizzes, setQuizzes] = useState([]);
  const [students, setStudents] = useState([]);
  const [grades, setGrades] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (user.role === 'lecturer') {
      fetchQuizzes();
      fetchStudents();
      fetchGrades();
    } else {
      fetchStudentQuizzes();
    }
  }, [user.role]);

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
    }
  };

  const downloadQuiz = async (quizId, format = 'pdf') => {
    try {
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
      }
    } catch (error) {
      console.error('Error downloading quiz:', error);
      alert('Failed to download quiz');
    }
  };

  const downloadGrades = async (format = 'excel') => {
    try {
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
        a.download = `grades.${format === 'excel' ? 'xlsx' : 'csv'}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (error) {
      console.error('Error downloading grades:', error);
      alert('Failed to download grades');
    }
  };

  const renderLecturerDashboard = () => (
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
          <span className="tab-icon">📝</span>
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
        {activeTab === 'create' && <CreateQuizTab />}
        {activeTab === 'quizzes' && <QuizzesTab quizzes={quizzes} onDownload={downloadQuiz} />}
        {activeTab === 'students' && <StudentsTab students={students} />}
        {activeTab === 'grades' && <GradesTab grades={grades} onDownload={downloadGrades} />}
      </div>
    </div>
  );

  const renderStudentDashboard = () => (
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
        {activeTab === 'available' && <AvailableQuizzesTab />}
        {activeTab === 'take' && <TakeQuizTab onStartQuiz={onStartQuiz} />}
        {activeTab === 'completed' && <CompletedQuizzesTab />}
        {activeTab === 'results' && <StudentResultsTab />}
      </div>
    </div>
  );

  return (
    <div className="dashboard-container">
      <div className="dashboard-background">
        <div className="animated-orbs">
          <div className="orb orb-1"></div>
          <div className="orb orb-2"></div>
          <div className="orb orb-3"></div>
        </div>
      </div>

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

      <main className="dashboard-main">
        {user.role === 'lecturer' ? renderLecturerDashboard() : renderStudentDashboard()}
      </main>
    </div>
  );
};

// Create Quiz Tab Component
const CreateQuizTab = () => {
  const [formData, setFormData] = useState({
    topic: '',
    numQuestions: 5,
    difficulty: 'medium',
    timeLimit: 30
  });

  const handleCreateQuiz = async (e) => {
    e.preventDefault();
    // Implementation for creating quiz
    console.log('Creating quiz:', formData);
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
              placeholder="Enter quiz topic"
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
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
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
        <button type="submit" className="create-btn">
          <span>✨</span>
          Generate Quiz
        </button>
      </form>
    </div>
  );
};

// Quizzes Tab Component
const QuizzesTab = ({ quizzes, onDownload }) => (
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
      {quizzes.map((quiz, index) => (
        <div key={index} className="quiz-card">
          <div className="quiz-header">
            <h3>{quiz.topic || `Quiz ${index + 1}`}</h3>
            <span className="quiz-date">Today</span>
          </div>
          <div className="quiz-details">
            <span>📝 5 Questions</span>
            <span>⏱️ 30 minutes</span>
            <span>🎯 Medium</span>
          </div>
          <div className="quiz-actions">
            <button 
              className="download-btn pdf"
              onClick={() => onDownload(index, 'pdf')}
            >
              📄 PDF
            </button>
            <button 
              className="download-btn word"
              onClick={() => onDownload(index, 'docx')}
            >
              📘 Word
            </button>
            <button className="share-btn">
              🔗 Share
            </button>
          </div>
        </div>
      ))}
    </div>
  </div>
);

// Students Tab Component
const StudentsTab = ({ students }) => (
  <div className="students-section">
    <h2>Registered Students</h2>
    <div className="students-grid">
      {students.map((student, index) => (
        <div key={index} className="student-card">
          <div className="student-avatar">
            {student.name ? student.name.charAt(0) : 'S'}
          </div>
          <div className="student-info">
            <h3>{student.name || `Student ${index + 1}`}</h3>
            <p>{student.email || 'student@example.com'}</p>
            <div className="student-stats">
              <span>✅ 5 Completed</span>
              <span>📊 85% Avg</span>
            </div>
          </div>
        </div>
      ))}
    </div>
  </div>
);

// Grades Tab Component
const GradesTab = ({ grades, onDownload }) => (
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
            <th>Quiz</th>
            <th>Score</th>
            <th>Date</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {grades.map((grade, index) => (
            <tr key={index}>
              <td>Student {index + 1}</td>
              <td>Math Quiz</td>
              <td>
                <span className="score-badge">85%</span>
              </td>
              <td>Today</td>
              <td>
                <button className="view-btn">👁️ View</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  </div>
);

// Student components
const AvailableQuizzesTab = () => (
  <div className="available-quizzes">
    <h2>Available Quizzes</h2>
    <div className="quiz-list">
      <div className="quiz-item">
        <h3>Mathematics Quiz</h3>
        <p>10 questions • 30 minutes</p>
        <div className="quiz-meta">
          <span className="difficulty medium">Medium</span>
          <span className="created-by">By: Prof. Smith</span>
        </div>
        <button className="take-quiz-btn">Start Quiz</button>
      </div>
      <div className="quiz-item">
        <h3>Science Quiz</h3>
        <p>15 questions • 45 minutes</p>
        <div className="quiz-meta">
          <span className="difficulty hard">Hard</span>
          <span className="created-by">By: Dr. Johnson</span>
        </div>
        <button className="take-quiz-btn">Start Quiz</button>
      </div>
    </div>
  </div>
);

const TakeQuizTab = ({ onStartQuiz }) => (
  <div className="take-quiz-section">
    <h2>Create Your Own Quiz</h2>
    <p>Generate a custom quiz on any topic you'd like to practice!</p>
    <button className="create-custom-quiz-btn" onClick={onStartQuiz}>
      <span>🎯</span>
      Create Custom Quiz
    </button>
  </div>
);

const CompletedQuizzesTab = () => (
  <div className="completed-quizzes">
    <h2>Completed Quizzes</h2>
    <p>No completed quizzes yet.</p>
  </div>
);

const StudentResultsTab = () => (
  <div className="student-results">
    <h2>My Results</h2>
    <p>No results available yet.</p>
  </div>
);

export default Dashboard;
