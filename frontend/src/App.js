import React, { useState } from "react";
import TopicSelector from "./components/TopicSelector";
import Quiz from "./components/Quiz";
import Scorecard from "./components/Scorecard";
import BookmarkList from "./components/BookmarkList";
import ModeSwitcher from "./components/ModeSwitcher";

function App() {
  const [mode, setMode] = useState("practice");
  const [started, setStarted] = useState(false);
  const [current, setCurrent] = useState(0);
  const [score, setScore] = useState(0);
  const [bookmarks, setBookmarks] = useState([]);
  const [showScore, setShowScore] = useState(false);
  const [questions, setQuestions] = useState([]);

  const startQuiz = async (topic) => {
    // Fetch questions from backend
    const res = await fetch("http://127.0.0.1:5000/api/quiz", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topic }),
    });
    const data = await res.json();
    setQuestions(data.questions);
    setStarted(true);
    setCurrent(0);
    setScore(0);
    setShowScore(false);
  };

  const handleAnswer = idx => {
    if (idx === questions[current].correctOption) setScore(score + 1);
    if (current + 1 < questions.length) setCurrent(current + 1);
    else setShowScore(true);
  };

  const bookmark = () => {
    setBookmarks([...bookmarks, questions[current]]);
  };

  return (
    <div>
      <h1>Quizgenix</h1>
      <ModeSwitcher mode={mode} setMode={setMode} />
      {!started && <TopicSelector onTopicSelected={startQuiz} />}
      {started && !showScore && questions.length > 0 && (
        <>
          <Quiz question={questions[current]} onAnswer={handleAnswer} />
          <button onClick={bookmark}>Bookmark</button>
        </>
      )}
      {showScore && (
        <Scorecard score={score} total={questions.length} onRestart={() => setStarted(false)} />
      )}
      <BookmarkList bookmarks={bookmarks} />
    </div>
  );
}

export default App;
