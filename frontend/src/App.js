import React, { useState } from "react";
import TopicSelector from "./components/TopicSelector";
import Quiz from "./components/Quiz";
import Scorecard from "./components/Scorecard";
import BookmarkList from "./components/BookmarkList";
import ModeSwitcher from "./components/ModeSwitcher";

function App() {
  const [mode, setMode] = useState("practice");
  const [started, setStarted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [bookmarks, setBookmarks] = useState([]);
  const [showScore, setShowScore] = useState(false);
  const [questions, setQuestions] = useState([]);
  const [scoreData, setScoreData] = useState(null);
  const [currentTopic, setCurrentTopic] = useState("");

  const startQuiz = async (topic, numQuestions = 5) => {
    setLoading(true);
    setCurrentTopic(topic);
    
    try {
      // Fetch questions from backend
      const res = await fetch("http://127.0.0.1:5000/api/quiz", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          topic: topic,
          num_questions: numQuestions 
        }),
      });
      
      if (!res.ok) {
        throw new Error('Failed to fetch questions');
      }
      
      const data = await res.json();
      setQuestions(data.questions);
      setStarted(true);
      setShowScore(false);
      setScoreData(null);
    } catch (error) {
      console.error('Error fetching questions:', error);
      alert('Failed to load quiz questions. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleQuizComplete = async (questions, userAnswers) => {
    setLoading(true);
    
    try {
      // Send answers to backend for scoring
      const res = await fetch("http://127.0.0.1:5000/api/score", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          questions: questions,
          user_answers: userAnswers,
          topic: currentTopic
        }),
      });
      
      if (!res.ok) {
        throw new Error('Failed to calculate score');
      }
      
      const scoreData = await res.json();
      setScoreData(scoreData);
      setShowScore(true);
    } catch (error) {
      console.error('Error calculating score:', error);
      alert('Failed to calculate score. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const bookmark = (question) => {
    const isAlreadyBookmarked = bookmarks.some(bm => 
      bm.question === question.question
    );
    
    if (!isAlreadyBookmarked) {
      setBookmarks([...bookmarks, question]);
    }
  };

  const restartQuiz = () => {
    setStarted(false);
    setShowScore(false);
    setQuestions([]);
    setScoreData(null);
    setCurrentTopic("");
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>🧠 Quizgenix</h1>
        <p className="app-subtitle">AI-Powered Quiz Generator</p>
      </header>

      <main className="app-main">
        <ModeSwitcher mode={mode} setMode={setMode} />
        
        {loading && (
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Loading your quiz...</p>
          </div>
        )}
        
        {!started && !loading && (
          <TopicSelector onTopicSelected={startQuiz} />
        )}
        
        {started && !showScore && !loading && questions.length > 0 && (
          <div className="quiz-section">
            <div className="quiz-header">
              <h2>📝 {currentTopic} Quiz</h2>
              <p>{questions.length} Questions</p>
            </div>
            <Quiz 
              questions={questions} 
              onQuizComplete={handleQuizComplete}
            />
          </div>
        )}
        
        {showScore && scoreData && (
          <Scorecard 
            scoreData={scoreData} 
            onRestart={restartQuiz} 
          />
        )}
        
        {bookmarks.length > 0 && (
          <BookmarkList bookmarks={bookmarks} />
        )}
      </main>
    </div>
  );
}

export default App;
