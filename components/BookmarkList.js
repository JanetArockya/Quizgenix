import React from "react";

export default function BookmarkList({ bookmarks }) {
  return (
    <div>
      <h2>Bookmarked Questions</h2>
      <ul>
        {bookmarks.map((q, i) => (
          <li key={i}>{q.question}</li>
        ))}
      </ul>
    </div>
  );
} 