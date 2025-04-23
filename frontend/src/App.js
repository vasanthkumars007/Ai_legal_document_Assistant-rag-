import React, { useState } from "react";
import UploadPDF from "./uploadpdf";
import LegalChat from "./legalchat";

function App() {
  const [summary, setSummary] = useState("");

  return (
    <div style={{ padding: "20px" }}>
      <h1>AI Legal Document Assistant</h1>
      <UploadPDF onSummary={setSummary} />
      {summary && (
        <>
          <h2>Summary:</h2>
          <p>{summary}</p>
          <LegalChat />
        </>
      )}
    </div>
  );
}

export default App;
