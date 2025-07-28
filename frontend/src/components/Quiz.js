import React, { useState, useEffect } from 'react';
import './Quiz.css';

const Quiz = ({ onComplete, onExit }) => {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [timeLeft, setTimeLeft] = useState(1800); // 30 minutes
  const [quizData, setQuizData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const savedQuiz = localStorage.getItem('currentQuiz');
    if (savedQuiz) {
      const quiz = JSON.parse(savedQuiz);
      setQuizData(quiz);
      setTimeLeft(quiz.time_limit || 1800);
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (timeLeft > 0) {
      const timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000);
      return () => clearTimeout(timer);
    } else {
      handleSubmitQuiz();
    }
  }, [timeLeft]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleAnswerSelect = (questionIndex, answer) => {
    setAnswers({
      ...answers,
      [questionIndex]: answer
    });
  };

  const handleSubmitQuiz = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/api/quiz/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          quiz_id: quizData.quiz_id,
          answers: answers
        })
      });

      if (response.ok) {
        const result = await response.json();
        localStorage.removeItem('currentQuiz');
        onComplete(result);
      }
    } catch (error) {
      console.error('Error submitting quiz:', error);
    }
  };

  if (loading) {
    return <div className="quiz-loading">Loading quiz...</div>;
  }

  if (!quizData || !quizData.questions) {
    return <div className="quiz-error">Quiz data not found</div>;
  }

  const question = quizData.questions[currentQuestion];

  return (
    <div className="quiz-container">
      <div className="quiz-header">
        <div className="quiz-info">
          <h1>{quizData.title}</h1>
          <div className="quiz-progress">
            Question {currentQuestion + 1} of {quizData.questions.length}
          </div>
        </div>
        <div className="quiz-timer">
          <span className="timer-icon">⏰</span>
          <span className={`timer-text ${timeLeft < 300 ? 'warning' : ''}`}>
            {formatTime(timeLeft)}
          </span>
        </div>
      </div>

      <div className="quiz-content">
        <div className="question-card">
          <h2 className="question-text">{question.question}</h2>
          
          <div className="answers-grid">
            {question.options.map((option, index) => (
              <button
                key={index}
                className={`answer-option ${answers[currentQuestion] === option ? 'selected' : ''}`}
                onClick={() => handleAnswerSelect(currentQuestion, option)}
              >
                <span className="option-letter">{String.fromCharCode(65 + index)}</span>
                <span className="option-text">{option}</span>
              </button>
            ))}
          </div>
        </div>

        <div className="quiz-navigation">
          <button 
            className="nav-btn prev"
            onClick={() => setCurrentQuestion(Math.max(0, currentQuestion - 1))}
            disabled={currentQuestion === 0}
          >
            ← Previous
          </button>
          
          <div className="question-dots">
            {quizData.questions.map((_, index) => (
              <button
                key={index}
                className={`dot ${index === currentQuestion ? 'active' : ''} ${answers[index] ? 'answered' : ''}`}
                onClick={() => setCurrentQuestion(index)}
              >
                {index + 1}
              </button>
            ))}
          </div>

          {currentQuestion < quizData.questions.length - 1 ? (
            <button 
              className="nav-btn next"
              onClick={() => setCurrentQuestion(currentQuestion + 1)}
            >
              Next →
            </button>
          ) : (
            <button 
              className="submit-btn"
              onClick={handleSubmitQuiz}
            >
              Submit Quiz
            </button>
          )}
        </div>
      </div>

      <div className="quiz-sidebar">
        <button className="exit-btn" onClick={onExit}>
          Exit Quiz
        </button>
        <div className="progress-summary">
          <h3>Progress</h3>
          <p>{Object.keys(answers).length} of {quizData.questions.length} answered</p>
          <div className="progress-bar">
            <div 
              className="progress-fill"
              style={{ width: `${(Object.keys(answers).length / quizData.questions.length) * 100}%` }}
            ></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Quiz;