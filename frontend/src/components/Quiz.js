import React from "react";

export default function Quiz({ question, onAnswer }) {
  if (!question) return null;
  return (
    <div>
      <h2>{question.question}</h2>
      {question.options.map((opt, idx) => (
        <button key={idx} onClick={() => onAnswer(idx)}>
          {opt}
        </button>
      ))}
    </div>
  );
} 