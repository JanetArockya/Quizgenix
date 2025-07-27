import React from "react";

export default function ModeSwitcher({ mode, setMode }) {
  return (
    <div>
      <button onClick={() => setMode("practice")}>Practice Mode</button>
      <button onClick={() => setMode("test")}>Test Mode</button>
      <p>Current mode: {mode}</p>
    </div>
  );
} 