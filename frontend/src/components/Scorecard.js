import React from "react";

export default function Scorecard({ score, total, onRestart }) {
  return (
    <div>
      <h2>Quiz Complete!</h2>
      <p>Your score: {score} / {total}</p>
      <button onClick={onRestart}>Restart</button>
    </div>
  );
} 