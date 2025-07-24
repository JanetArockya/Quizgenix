import React, { useState } from "react";

export default function Quiz({ questions, onQuizComplete }) {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [userAnswers, setUserAnswers] = useState([]);
  const [showProgress, setShowProgress] = useState(true);

  if (!questions || questions.length === 0) return null;

  const currentQuestion = questions[currentQuestionIndex];
  const isLastQuestion = currentQuestionIndex === questions.length - 1;
  const progress = ((currentQuestionIndex + 1) / questions.length) * 100;

  const handleAnswer = (selectedOption) => {
    const newAnswers = [...userAnswers, selectedOption];
    setUserAnswers(newAnswers);

    if (isLastQuestion) {
      // Quiz completed - send results for scoring
      onQuizComplete(questions, newAnswers);
    } else {
      // Move to next question
      setTimeout(() => {
        setCurrentQuestionIndex(currentQuestionIndex + 1);
      }, 500);
    }
  };

  return (
    <div className="quiz-container">
      {/* Progress Bar */}
      {showProgress && (
        <div className="progress-container">
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${progress}%` }}
            ></div>
          </div>
          <span className="progress-text">
            Question {currentQuestionIndex + 1} of {questions.length}
          </span>
        </div>
      )}

      {/* Question */}
      <div className="question-container">
        <h2 className="question-title">
          {currentQuestion.question}
        </h2>
        
        {/* Question Meta Info */}
        <div className="question-meta">
          {currentQuestion.difficulty && (
            <span className={`difficulty ${currentQuestion.difficulty}`}>
              {currentQuestion.difficulty.toUpperCase()}
            </span>
          )}
          {currentQuestion.ai_generated && (
            <span className="ai-badge">🤖 AI Generated</span>
          )}
        </div>

        {/* Options */}
        <div className="options-container">
          {currentQuestion.options.map((option, index) => (
            <button 
              key={index} 
              className="option-button"
              onClick={() => handleAnswer(index)}
            >
              <span className="option-letter">
                {String.fromCharCode(65 + index)}
              </span>
              <span className="option-text">{option}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Question Counter */}
      <div className="question-counter">
        {questions.map((_, index) => (
          <div 
            key={index} 
            className={`counter-dot ${index === currentQuestionIndex ? 'active' : ''} ${index < currentQuestionIndex ? 'completed' : ''}`}
          ></div>
        ))}
      </div>
    </div>
  );
} 