import React, { useState, useEffect, useRef } from 'react';
import './QuizTaking.css';

const QuizTaking = ({ quizId, onComplete, onCancel }) => {
  const [quizData, setQuizData] = useState(null);
  const [sessionToken, setSessionToken] = useState(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [timeLeft, setTimeLeft] = useState(7200); // 2 hours
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState('');
  const [showConfirmSubmit, setShowConfirmSubmit] = useState(false);
  const timerRef = useRef(null);

  useEffect(() => {
    startQuiz();
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, []);

  useEffect(() => {
    if (sessionToken && timeLeft > 0) {
      timerRef.current = setInterval(() => {
        setTimeLeft(prev => {
          if (prev <= 1) {
            handleSubmitQuiz(true); // Auto-submit when time runs out
            return 0;
          }
          return prev - 1;
        });
      }, 1000);

      return () => clearInterval(timerRef.current);
    }
  }, [sessionToken]);

  const startQuiz = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://127.0.0.1:5000/api/quiz/${quizId}/start`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      const data = await response.json();
      if (response.ok) {
        setQuizData(data.quiz);
        setSessionToken(data.session_token);
        setTimeLeft(data.time_limit);
        setMessage('Quiz started! Good luck! 🍀');
        setTimeout(() => setMessage(''), 3000);
      } else {
        setMessage(`❌ Error: ${data.error}`);
      }
    } catch (error) {
      setMessage('❌ Network error starting quiz');
    }
    setLoading(false);
  };

  const handleAnswerSelect = async (answerIndex) => {
    const questionId = quizData.questions[currentQuestionIndex].id;
    const newAnswers = { ...answers, [questionId]: answerIndex };
    setAnswers(newAnswers);

    // Submit answer to backend
    try {
      await fetch(`http://127.0.0.1:5000/api/quiz/session/${sessionToken}/answer`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          question_id: questionId,
          answer: answerIndex
        })
      });
    } catch (error) {
      console.error('Error saving answer:', error);
    }
  };

  const handleSubmitQuiz = async (isAutoSubmit = false) => {
    if (!isAutoSubmit && Object.keys(answers).length < quizData.questions.length) {
      const unanswered = quizData.questions.length - Object.keys(answers).length;
      if (!window.confirm(`You have ${unanswered} unanswered questions. Submit anyway?`)) {
        return;
      }
    }

    setSubmitting(true);
    try {
      const response = await fetch(`http://127.0.0.1:5000/api/quiz/session/${sessionToken}/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      const data = await response.json();
      if (response.ok) {
        onComplete(data.results);
      } else {
        setMessage(`❌ Error: ${data.error}`);
      }
    } catch (error) {
      setMessage('❌ Network error submitting quiz');
    }
    setSubmitting(false);
  };

  const formatTime = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getTimeColor = () => {
    if (timeLeft < 300) return '#dc3545'; // Red for < 5 minutes
    if (timeLeft < 900) return '#ffc107'; // Yellow for < 15 minutes
    return '#28a745'; // Green
  };

  if (loading) {
    return (
      <div className="quiz-taking loading">
        <div className="loading-spinner"></div>
        <p>Starting quiz...</p>
      </div>
    );
  }

  if (!quizData) {
    return (
      <div className="quiz-taking error">
        <h2>❌ Quiz Not Available</h2>
        <p>{message}</p>
        <button onClick={onCancel} className="btn btn-secondary">
          Back to Dashboard
        </button>
      </div>
    );
  }

  const currentQuestion = quizData.questions[currentQuestionIndex];
  const progress = ((currentQuestionIndex + 1) / quizData.questions.length) * 100;

  return (
    <div className="quiz-taking">
      {message && (
        <div className={`message ${message.includes('❌') ? 'error' : 'success'}`}>
          {message}
        </div>
      )}

      <div className="quiz-header">
        <div className="quiz-info">
          <h1>📝 {quizData.title}</h1>
          <div className="quiz-meta">
            <span>📖 {quizData.subject}</span>
            <span>🎯 {quizData.topic}</span>
            <span className={`difficulty ${quizData.difficulty}`}>
              {quizData.difficulty === 'easy' ? '🟢' : quizData.difficulty === 'medium' ? '🟡' : '🔴'} {quizData.difficulty}
            </span>
          </div>
        </div>

        <div className="quiz-controls">
          <div className="timer" style={{ color: getTimeColor() }}>
            ⏱️ {formatTime(timeLeft)}
          </div>
          <div className="question-counter">
            Question {currentQuestionIndex + 1} of {quizData.questions.length}
          </div>
        </div>
      </div>

      <div className="progress-bar">
        <div className="progress-fill" style={{ width: `${progress}%` }}></div>
      </div>

      <div className="question-container">
        <div className="question-header">
          <h2>Q{currentQuestionIndex + 1}: {currentQuestion.question}</h2>
        </div>

        <div className="options-container">
          {currentQuestion.options.map((option, index) => (
            <div 
              key={index}
              className={`option ${answers[currentQuestion.id] === index ? 'selected' : ''}`}
              onClick={() => handleAnswerSelect(index)}
            >
              <div className="option-radio">
                {answers[currentQuestion.id] === index && <div className="radio-selected"></div>}
              </div>
              <div className="option-content">
                <span className="option-letter">{String.fromCharCode(65 + index)}</span>
                <span className="option-text">{option}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="navigation-controls">
        <div className="nav-buttons">
          <button 
            onClick={() => setCurrentQuestionIndex(Math.max(0, currentQuestionIndex - 1))}
            disabled={currentQuestionIndex === 0}
            className="btn btn-secondary"
          >
            ← Previous
          </button>
          
          {currentQuestionIndex < quizData.questions.length - 1 ? (
            <button 
              onClick={() => setCurrentQuestionIndex(currentQuestionIndex + 1)}
              className="btn btn-primary"
            >
              Next →
            </button>
          ) : (
            <button 
              onClick={() => setShowConfirmSubmit(true)}
              className="btn btn-success"
              disabled={submitting}
            >
              {submitting ? '📤 Submitting...' : '🎯 Submit Quiz'}
            </button>
          )}
        </div>

        <div className="answer-status">
          <span>Answered: {Object.keys(answers).length}/{quizData.questions.length}</span>
          <div className="question-indicators">
            {quizData.questions.map((q, index) => (
              <div 
                key={index}
                className={`indicator ${answers[q.id] !== undefined ? 'answered' : ''} ${index === currentQuestionIndex ? 'current' : ''}`}
                onClick={() => setCurrentQuestionIndex(index)}
              >
                {index + 1}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Confirm Submit Modal */}
      {showConfirmSubmit && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h3>🎯 Submit Quiz?</h3>
            <p>
              You have answered <strong>{Object.keys(answers).length}</strong> out of <strong>{quizData.questions.length}</strong> questions.
            </p>
            {Object.keys(answers).length < quizData.questions.length && (
              <p className="warning">
                ⚠️ You have <strong>{quizData.questions.length - Object.keys(answers).length}</strong> unanswered questions.
              </p>
            )}
            <p>Are you sure you want to submit your quiz?</p>
            <div className="modal-actions">
              <button 
                onClick={() => setShowConfirmSubmit(false)}
                className="btn btn-secondary"
              >
                Cancel
              </button>
              <button 
                onClick={() => {
                  setShowConfirmSubmit(false);
                  handleSubmitQuiz();
                }}
                className="btn btn-success"
                disabled={submitting}
              >
                {submitting ? 'Submitting...' : 'Yes, Submit'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default QuizTaking;