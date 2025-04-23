import React, { useState } from "react";
import { askQuestion } from "./api";

export default function LegalChat() {
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState("");

  const handleAsk = async () => {
    const result = await askQuestion(query);
    setAnswer(result.answer);
  };

  return (
    <div>
      <textarea value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Ask a legal question..." />
      <button onClick={handleAsk}>Ask</button>
      <p><strong>Answer:</strong> {answer}</p>
    </div>
  );
}
