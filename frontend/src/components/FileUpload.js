import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';

function FileUpload({ onUpload, loading }) {
  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      onUpload(acceptedFiles[0]);
    }
  }, [onUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/json': ['.json'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
    },
    multiple: false,
  });

  return (
    <div style={{
      background: 'rgba(255, 255, 255, 0.1)',
      backdropFilter: 'blur(10px)',
      border: '2px dashed rgba(255, 255, 255, 0.3)',
      borderRadius: '20px',
      padding: '3rem',
      textAlign: 'center',
      color: 'white',
      cursor: 'pointer',
      transition: 'all 0.3s ease',
      minWidth: '400px',
      maxWidth: '600px',
    }}>
      <div {...getRootProps()}>
        <input {...getInputProps()} />
        {loading ? (
          <div>
            <p style={{ fontSize: '1.2rem', marginBottom: '20px' }}>Analyzing your data...</p>
            <div style={{
              width: '50px',
              height: '50px',
              border: '3px solid rgba(255, 255, 255, 0.3)',
              borderTop: '3px solid white',
              borderRadius: '50%',
              margin: '0 auto',
              animation: 'spin 1s linear infinite',
            }} />
          </div>
        ) : isDragActive ? (
          <div>
            <p style={{ fontSize: '3rem', marginBottom: '1rem' }}>📁</p>
            <h3>Drop your file here</h3>
            <p>Release to analyze</p>
          </div>
        ) : (
          <div>
            <p style={{ fontSize: '3rem', marginBottom: '1rem' }}>📊</p>
            <h3>Upload Your Dataset</h3>
            <p>Drag and drop or click to select</p>
            <p style={{ fontSize: '0.9rem', opacity: 0.8, marginTop: '0.5rem' }}>
              Supports CSV, JSON, and Excel files
            </p>
          </div>
        )}
      </div>
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

export default FileUpload;