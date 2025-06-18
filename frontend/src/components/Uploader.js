import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';

export default function Uploader({ onUpload, loading }) {
  const onDrop = useCallback(acceptedFiles => {
    if (acceptedFiles.length > 0) {
      onUpload(acceptedFiles[0]);
    }
  }, [onUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    maxFiles: 1,
    disabled: loading
  });

  return (
    <div {...getRootProps()} 
         className={`upload-container ${isDragActive ? 'active' : ''}`}>
      <input {...getInputProps()} />
      
      <div className="upload-content">
        {loading ? (
          <div className="loader">Processing PDF...</div>
        ) : (
          <>
            <div className="upload-icon">📄</div>
            <h3>Upload Policy Document</h3>
            <p>Drag & drop PDF or click to browse</p>
            <p className="hint">(Works best with reports, white papers, policy documents)</p>
          </>
        )}
      </div>
    </div>
  );
}
