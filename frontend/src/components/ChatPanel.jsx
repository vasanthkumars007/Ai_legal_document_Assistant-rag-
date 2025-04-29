import React, { useState } from 'react';
import {
  Paper,
  Box,
  Typography,
  TextField,
  IconButton,
  Stack,
} from '@mui/material';
import KeyboardVoiceIcon from '@mui/icons-material/KeyboardVoice';
import SendIcon from '@mui/icons-material/Send';

const ChatPanel = ({ summary }) => {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([
    { sender: 'bot', text: 'Hello! I’m ready to help you analyze your legal document.' }
  ]);

  const handleSend = async () => {
    if (!query.trim()) return;

    setMessages(prev => [...prev, { sender: 'user', text: query }]);

    try {
      const formData = new FormData();
      formData.append('query', query);

      const res = await fetch('http://localhost:8000/legal_chat/', {
        method: 'POST',
        body: formData,
      });

      const data = await res.json();

      setMessages(prev => [
        ...prev,
        { sender: 'bot', text: data.answer || 'Sorry, I could not understand that.' },
      ]);
    } catch (err) {
      console.error('Chat request failed', err);
      setMessages(prev => [
        ...prev,
        { sender: 'bot', text: 'There was an error. Please try again later.' },
      ]);
    }

    setQuery('');
  };

  return (
    <Paper sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box
        p={2}
        borderBottom={1}
        borderColor="divider"
        flexGrow={1}
        overflow="auto"
      >
        {summary ? (
          <Stack spacing={2}>
            {messages.map((msg, index) => (
              <Box
                key={index}
                alignSelf={msg.sender === 'user' ? 'flex-end' : 'flex-start'}
                bgcolor={msg.sender === 'user' ? 'primary.main' : 'grey.200'}
                color={msg.sender === 'user' ? 'white' : 'black'}
                px={2}
                py={1}
                borderRadius={2}
                maxWidth="80%"
              >
                <Typography variant="body2">{msg.text}</Typography>
              </Box>
            ))}
          </Stack>
        ) : (
          <Typography variant="body1" color="text.secondary">
            Upload a document to start chatting.
          </Typography>
        )}
      </Box>

      <Box
        p={2}
        borderTop={1}
        borderColor="divider"
        display="flex"
        gap={1}
        alignItems="center"
      >
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Ask about specific clauses, dates, parties involved..."
          disabled={!summary}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
        />
        <IconButton onClick={handleSend} disabled={!summary}>
          <SendIcon />
        </IconButton>
        <IconButton disabled>
          <KeyboardVoiceIcon />
        </IconButton>
      </Box>
    </Paper>
  );
};

export default ChatPanel;
