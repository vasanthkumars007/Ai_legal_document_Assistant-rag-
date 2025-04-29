import React, { useState } from 'react';
import { Box } from '@mui/material';
import Header from './components/Header';
import UploadArea from './components/UploadArea';
import DocumentSummary from './components/DocumentSummary';
import ChatPanel from './components/ChatPanel';

const App = () => {
  const [summary, setSummary] = useState('');
  const [chatHistory, setChatHistory] = useState([]);

  const HEADER_HEIGHT = 64;
  const UPLOAD_HEIGHT = 200;

  const handleSummaryUpdate = (newSummary) => {
    setSummary(newSummary);
    setChatHistory([]); 
  };

  const handleSendMessage = async (message) => {
    const formData = new FormData();
    formData.append('query', message);

    try {
      const res = await fetch('http://localhost:8000/legal_chat/', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      const answer = data.answer || 'No answer received';
      setChatHistory((prev) => [...prev, { message, answer }]);
    } catch (err) {
      console.error('Chat failed', err);
    }
  };

  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ height: HEADER_HEIGHT, flexShrink: 0 }}>
        <Header />
      </Box>

      <Box sx={{ height: UPLOAD_HEIGHT, flexShrink: 0, px: 3, py: 2 }}>
        <UploadArea onSummaryUpdate={handleSummaryUpdate} />
      </Box>

      <Box sx={{ flexGrow: 1, px: 7, mt: '-1%' }}>
        <Box sx={{ display: 'flex', height: '100%', width: '100%', gap: 3 }}>
          <Box sx={{ width: '30%' }}>
            <DocumentSummary summary={summary} />
          </Box>
          <Box sx={{ width: '70%' }}>
            <ChatPanel chatHistory={chatHistory} onSendMessage={handleSendMessage} summary={summary} />
          </Box>
        </Box>
      </Box>
    </Box>
  );
};

export default App;
