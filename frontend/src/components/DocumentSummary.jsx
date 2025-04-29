import React from 'react';
import { Paper, Box, Typography } from '@mui/material';

const DocumentSummary = ({ summary }) => {
  return (
    <Paper sx={{ height: '100%', p: 2, overflowY: 'auto' }}>
      <Typography variant="h6" gutterBottom>
        Document Summary
      </Typography>
      {summary ? (
        <Typography variant="body2">{summary}</Typography>
      ) : (
        <Typography variant="body2" color="text.secondary">
          No summary available. Please upload a document to see the summary.
        </Typography>
      )}
    </Paper>
  );
};

export default DocumentSummary;
