import React, { useState } from "react";
import { uploadPdf } from "./api";

export default function UploadPDF({ onSummary }) {
  const [file, setFile] = useState(null);

  const handleUpload = async () => {
    const result = await uploadPdf(file);
    onSummary(result.summary);
  };

  return (
    <div>
      <input type="file" onChange={(e) => setFile(e.target.files[0])} />
      <button onClick={handleUpload}>Upload and Summarize</button>
    </div>
  );
}
