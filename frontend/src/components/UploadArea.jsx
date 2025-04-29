import React, { useRef } from 'react';
import { Box, Typography, Paper, IconButton } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';

const UploadArea = ({ onSummaryUpdate }) => {
  const fileInputRef = useRef();

  const handleUpload = async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/summary/', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      onSummaryUpdate(data.summary);
    } catch (err) {
      console.error('Upload failed', err);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) handleUpload(file);
  };

  const handleClick = () => {
    fileInputRef.current.click();
  };

  return (
    <Paper
      variant="outlined"
      sx={{
        p: 4,
        textAlign: 'center',
        borderStyle: 'dashed',
        bgcolor: '#f9f9f9',
        cursor: 'pointer',
      }}
      onClick={handleClick}
    >
      <input
        type="file"
        accept=".pdf,.docx,.txt"
        hidden
        ref={fileInputRef}
        onChange={handleFileChange}
      />
      <IconButton disableRipple>
        <CloudUploadIcon sx={{ fontSize: 40 }} />
      </IconButton>
      <Typography variant="h6">Drag and drop your legal document here</Typography>
      <Typography variant="body2" color="text.secondary">
        or click to browse
      </Typography>
      <Typography variant="caption" color="text.disabled" display="block" mt={1}>
        Supported formats: .pdf .......
      </Typography>
    </Paper>
  );
};

export default UploadArea;
