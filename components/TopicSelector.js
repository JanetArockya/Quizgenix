import React, { useState } from "react";

export default function TopicSelector({ onTopicSelected }) {
  const [topic, setTopic] = useState("");
  const [numQuestions, setNumQuestions] = useState(5);

  const popularTopics = [
    "JavaScript Programming",
    "World History", 
    "Science",
    "Mathematics",
    "Geography",
    "Literature",
    "Technology",
    "Art History",
    "Biology",
    "Physics"
  ];

  const handleStart = () => {
    if (topic.trim()) {
      onTopicSelected(topic.trim(), numQuestions);
    }
  };

  const handleTopicClick = (selectedTopic) => {
    setTopic(selectedTopic);
  };

  return (
    <div className="topic-selector">
      <div className="selector-header">
        <h2>🎯 Choose Your Quiz Topic</h2>
        <p>Enter a topic or select from popular choices below</p>
      </div>

      <div className="input-section">
        <div className="input-group">
          <label htmlFor="topic-input">Topic:</label>
          <input
            id="topic-input"
            type="text"
            value={topic}
            onChange={e => setTopic(e.target.value)}
            placeholder="e.g., React.js, Ancient Rome, Quantum Physics..."
            className="topic-input"
            onKeyPress={(e) => e.key === 'Enter' && handleStart()}
          />
        </div>

        <div className="input-group">
          <label htmlFor="num-questions">Number of Questions:</label>
          <select
            id="num-questions"
            value={numQuestions}
            onChange={e => setNumQuestions(parseInt(e.target.value))}
            className="questions-select"
          >
            <option value={3}>3 Questions (Quick)</option>
            <option value={5}>5 Questions (Standard)</option>
            <option value={10}>10 Questions (Extended)</option>
            <option value={15}>15 Questions (Comprehensive)</option>
            <option value={20}>20 Questions (Challenge)</option>
          </select>
        </div>

        <button 
          onClick={handleStart}
          disabled={!topic.trim()}
          className="start-button"
        >
          🚀 Start Quiz ({numQuestions} questions)
        </button>
      </div>

      <div className="popular-topics">
        <h3>💡 Popular Topics</h3>
        <div className="topics-grid">
          {popularTopics.map((popularTopic, index) => (
            <button
              key={index}
              onClick={() => handleTopicClick(popularTopic)}
              className={`topic-chip ${topic === popularTopic ? 'selected' : ''}`}
            >
              {popularTopic}
            </button>
          ))}
        </div>
      </div>

      <div className="features-info">
        <div className="feature">
          <span className="feature-icon">🤖</span>
          <span>AI-Generated Questions</span>
        </div>
        <div className="feature">
          <span className="feature-icon">📊</span>
          <span>Detailed Score Analysis</span>
        </div>
        <div className="feature">
          <span className="feature-icon">📚</span>
          <span>Study Resources Included</span>
        </div>
        <div className="feature">
          <span className="feature-icon">💯</span>
          <span>100% Free</span>
        </div>
      </div>
    </div>
  );
} 