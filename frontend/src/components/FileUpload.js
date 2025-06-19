import React, { useState } from 'react';

const FileUpload = ({ onAnalysisComplete }) => {
  const [isProcessing, setIsProcessing] = useState(false);

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setIsProcessing(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      // Use Render URL in production, localhost in development
      const backendUrl = process.env.NODE_ENV === 'production' 
        ? 'https://your-render-backend-url/upload' 
        : 'http://localhost:5000/upload';
        
      const response = await fetch(backendUrl, {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }
      
      const data = await response.json();
      onAnalysisComplete(data);
    } catch (error) {
      console.error('Error:', error);
      alert('Analysis failed. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="upload-container">
      <label className="upload-label">
        {isProcessing ? 'Processing...' : 'Upload Policy Document'}
        <input 
          type="file" 
          accept=".pdf" 
          onChange={handleFileChange}
          disabled={isProcessing}
          hidden
        />
      </label>
      <p className="file-hint">PDF files only (max 10MB)</p>
    </div>
  );
};

export default FileUpload;
