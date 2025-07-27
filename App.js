import React, { useState, useEffect } from "react";
import Login from "./components/Login";
import Dashboard from "./components/Dashboard";
import TopicSelector from "./components/TopicSelector";
import Quiz from "./components/Quiz";
import Scorecard from "./components/Scorecard";
import BookmarkList from "./components/BookmarkList";
import ModeSwitcher from "./components/ModeSwitcher";

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [mode, setMode] = useState("practice");
  const [started, setStarted] = useState(false);
  const [quizLoading, setQuizLoading] = useState(false);
  const [bookmarks, setBookmarks] = useState([]);
  const [showScore, setShowScore] = useState(false);
  const [questions, setQuestions] = useState([]);
  const [scoreData, setScoreData] = useState(null);
  const [currentTopic, setCurrentTopic] = useState("");
  const [showQuizInterface, setShowQuizInterface] = useState(false);

  // Check for existing authentication on app load
  useEffect(() => {
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');
    
    if (token && userData) {
      try {
        const parsedUser = JSON.parse(userData);
        setUser(parsedUser);
      } catch (error) {
        console.error('Error parsing user data:', error);
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      }
    }
    setLoading(false);
  }, []);

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
    setStarted(false);
    setShowScore(false);
    setShowQuizInterface(false);
    setQuestions([]);
    setScoreData(null);
  };

  const startQuiz = async (topic, numQuestions = 5) => {
    setQuizLoading(true);
    setCurrentTopic(topic);
    
    try {
      // Fetch questions from backend
      const res = await fetch("http://127.0.0.1:5000/api/quiz", {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${localStorage.getItem('token')}`
        },
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
      setShowQuizInterface(false); // Show quiz taking interface
    } catch (error) {
      console.error('Error fetching questions:', error);
      alert('Failed to load quiz questions. Please try again.');
    } finally {
      setQuizLoading(false);
    }
  };

  const handleQuizComplete = async (questions, userAnswers) => {
    setLoading(true);
    
    try {
      // Send answers to backend for scoring
      const res = await fetch("http://127.0.0.1:5000/api/score", {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          questions: questions,
          user_answers: userAnswers,
          topic: currentTopic,
          user_id: user?.id
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
    setShowQuizInterface(true); // Go back to topic selection
  };

  const goBackToDashboard = () => {
    setStarted(false);
    setShowScore(false);
    setQuestions([]);
    setScoreData(null);
    setCurrentTopic("");
    setShowQuizInterface(false); // Go back to dashboard
  };

  // Show loading screen while checking authentication
  if (loading) {
    return (
      <div className="app">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  // Show login if user is not authenticated
  if (!user) {
    return <Login onLogin={handleLogin} />;
  }

  // Main authenticated app interface
  return (
    <div className="app">
      {!showQuizInterface && !started && !showScore && (
        <Dashboard 
          user={user} 
          onLogout={handleLogout}
          onStartQuiz={() => setShowQuizInterface(true)}
        />
      )}

      {showQuizInterface && !started && !showScore && (
        <>
          <header className="app-header">
            <h1>🧠 Quizgenix</h1>
            <p className="app-subtitle">AI-Powered Quiz Generator</p>
            <button 
              className="back-to-dashboard-btn"
              onClick={goBackToDashboard}
            >
              ← Back to Dashboard
            </button>
          </header>
          <main className="app-main">
            <ModeSwitcher mode={mode} setMode={setMode} />
            {quizLoading ? (
              <div className="loading-container">
                <div className="loading-spinner"></div>
                <p>Generating your quiz...</p>
              </div>
            ) : (
              <TopicSelector onTopicSelected={startQuiz} />
            )}
          </main>
        </>
      )}

      {started && !showScore && (
        <>
          <header className="app-header">
            <h1>🧠 Quizgenix</h1>
            <p className="app-subtitle">Topic: {currentTopic}</p>
          </header>
          <main className="app-main">
            <div className="quiz-section">
              <div className="quiz-header">
                <h2>📝 {currentTopic} Quiz</h2>
                <p>{questions.length} Questions • AI Generated</p>
              </div>
              <Quiz 
                questions={questions} 
                onQuizComplete={handleQuizComplete}
              />
            </div>
          </main>
        </>
      )}

      {showScore && scoreData && (
        <>
          <header className="app-header">
            <h1>🧠 Quizgenix</h1>
            <p className="app-subtitle">Quiz Complete!</p>
          </header>
          <main className="app-main">
            <Scorecard 
              scoreData={scoreData} 
              onRestart={restartQuiz}
              onBackToDashboard={goBackToDashboard}
            />
          </main>
        </>
      )}
    </div>
  );
}

export default App;
