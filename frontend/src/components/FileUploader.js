
import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload } from 'lucide-react';
import axios from 'axios';

const FileUploader = ({ onAnalysisStart, onAnalysisComplete }) => {
  const onDrop = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (!file) return;

    onAnalysisStart();
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_id', 'user_' + Date.now());

    try {
      const response = await axios.post('http://localhost:8000/api/upload', formData);
      onAnalysisComplete(response.data);
    } catch (error) {
      console.error('Upload error:', error);
      alert('Error analyzing data. Please try again.');
      onAnalysisStart(false);
    }
  }, [onAnalysisStart, onAnalysisComplete]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.ms-excel': ['.xlsx']
    }
  });

  return (
    <div {...getRootProps()} className="uploader-container">
      <input {...getInputProps()} />
      <div className="upload-area">
        <Upload size={48} className="upload-icon" />
        {isDragActive ? (
          <p>Drop your CSV/Excel file here...</p>
        ) : (
          <>
            <p>Drag & drop your dataset here</p>
            <p className="upload-hint">or click to browse</p>
            <small>Supports CSV, Excel files</small>
          </>
        )}
      </div>
    </div>
  );
};

export default FileUploader;