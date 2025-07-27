import React, { useState } from "react";

export default function Scorecard({ scoreData, onRestart, onBackToDashboard }) {
  const [showDetails, setShowDetails] = useState(false);
  const [showResources, setShowResources] = useState(false);

  if (!scoreData) return null;

  const { score, results, study_resources } = scoreData;

  const getPerformanceColor = (percentage) => {
    if (percentage >= 90) return '#4CAF50'; // Green
    if (percentage >= 70) return '#2196F3'; // Blue  
    if (percentage >= 50) return '#FF9800'; // Orange
    return '#F44336'; // Red
  };

  return (
    <div className="scorecard-container">
      {/* Main Score Display */}
      <div className="score-header">
        <h2>🎉 Quiz Complete!</h2>
        <div className="score-circle" style={{ borderColor: getPerformanceColor(score.percentage) }}>
          <span className="score-percentage">{score.percentage}%</span>
          <span className="score-fraction">{score.correct}/{score.total}</span>
        </div>
        <p className="performance-message">{score.performance}</p>
      </div>

      {/* Action Buttons */}
      <div className="score-actions">
        <button className="btn btn-primary" onClick={onRestart}>
          🔄 Take Another Quiz
        </button>
        <button className="btn btn-primary" onClick={onBackToDashboard}>
          🏠 Back to Dashboard
        </button>
        <button 
          className="btn btn-secondary" 
          onClick={() => setShowDetails(!showDetails)}
        >
          📊 {showDetails ? 'Hide' : 'Show'} Details
        </button>
        <button 
          className="btn btn-secondary" 
          onClick={() => setShowResources(!showResources)}
        >
          📚 Study Resources
        </button>
      </div>

      {/* Detailed Results */}
      {showDetails && (
        <div className="results-details">
          <h3>Question Review</h3>
          {results.map((result, index) => (
            <div key={index} className={`result-item ${result.is_correct ? 'correct' : 'incorrect'}`}>
              <div className="result-header">
                <span className="question-number">Q{result.questionId}</span>
                <span className={`result-status ${result.is_correct ? 'correct' : 'incorrect'}`}>
                  {result.is_correct ? '✅ Correct' : '❌ Incorrect'}
                </span>
              </div>
              
              <p className="result-question">{result.question}</p>
              
              <div className="result-answers">
                <div className="answer-row">
                  <strong>Your answer:</strong> 
                  <span className={result.is_correct ? 'correct-answer' : 'wrong-answer'}>
                    {result.options[result.user_answer]} 
                    ({String.fromCharCode(65 + result.user_answer)})
                  </span>
                </div>
                
                {!result.is_correct && (
                  <div className="answer-row">
                    <strong>Correct answer:</strong> 
                    <span className="correct-answer">
                      {result.options[result.correct_answer]} 
                      ({String.fromCharCode(65 + result.correct_answer)})
                    </span>
                  </div>
                )}
              </div>
              
              <p className="result-explanation">{result.explanation}</p>
              
              {result.source && (
                <a 
                  href={result.source} 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="source-link"
                >
                  📖 Learn More
                </a>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Study Resources */}
      {showResources && study_resources && (
        <div className="study-resources">
          <h3>📚 Study Resources</h3>
          <div className="resources-grid">
            {study_resources.map((resource, index) => (
              <div key={index} className="resource-card">
                <div className="resource-header">
                  <span className="resource-type">{resource.type}</span>
                </div>
                <h4 className="resource-title">{resource.title}</h4>
                <a 
                  href={resource.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="resource-link"
                >
                  Visit Resource →
                </a>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
} 