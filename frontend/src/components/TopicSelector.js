import React, { useState } from "react";

export default function TopicSelector({ onTopicSelected }) {
  const [topic, setTopic] = useState("");
  return (
    <div>
      <h2>Select a Topic</h2>
      <input
        value={topic}
        onChange={e => setTopic(e.target.value)}
        placeholder="Enter topic"
      />
      <button onClick={() => onTopicSelected(topic)}>Start Quiz</button>
    </div>
  );
} 