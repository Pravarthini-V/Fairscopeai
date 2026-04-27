import React, { useState } from 'react';
import axios from 'axios';
import { RefreshCw, Check, X, Download, TrendingUp, FileDown } from 'lucide-react';

const CorrectionModal = ({ result, onClose, onCorrect }) => {
  const [correcting, setCorrecting] = useState(false);
  const [correctionMethod, setCorrectionMethod] = useState('Reset Data (Remove Bias)');
  const [correctedData, setCorrectedData] = useState(null);
  const [showDownload, setShowDownload] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState(null);

  const correctionMethods = [
    { value: 'Reset Data (Remove Bias)', description: 'Balances approval rates across all groups by adjusting outcomes' },
    { value: 'Reweight Samples', description: 'Applies statistical weights to balance groups' },
    { value: 'Resample Data', description: 'Uses oversampling/undersampling techniques' }
  ];

  const handleCorrect = async () => {
    setCorrecting(true);
    try {
      const response = await axios.post('http://localhost:8000/api/correct', {
        session_id: result.session_id,
        method: correctionMethod,
        sensitive_attribute: result.sensitive_attributes?.[0] || 'gender',
        target_column: result.target_column || 'approved',
        user_id: result.user_id
      });
      
      console.log('Correction response:', response.data);
      
      if (response.data.status === 'success') {
        setCorrectedData(response.data);
        setDownloadUrl(response.data.download_url);
        setShowDownload(true);
        
        // Call onCorrect with updated data
        onCorrect({
          ...result,
          fairness_score: response.data.new_fairness_score,
          is_fair: response.data.is_fair,
          metrics: response.data.metrics,
          explanation: response.data.explanation,
          is_corrected: true
        });
      }
    } catch (error) {
      console.error('Correction error:', error);
      alert(`Correction failed: ${error.response?.data?.detail || error.message}`);
    } finally {
      setCorrecting(false);
    }
  };

  const handleDownload = async () => {
    if (!downloadUrl) {
      alert('No corrected data available to download');
      return;
    }
    
    try {
      console.log('Downloading from:', `http://localhost:8000${downloadUrl}`);
      const response = await axios.get(`http://localhost:8000${downloadUrl}`, {
        responseType: 'blob'
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      const filename = `corrected_${result.filename || 'dataset'}_${correctionMethod.replace(/\s/g, '_')}.csv`;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      alert('✅ File downloaded successfully!');
    } catch (error) {
      console.error('Download error:', error);
      alert('Failed to download corrected file. Please try again.');
    }
  };

  if (showDownload && correctedData) {
    return (
      <div className="modal-overlay">
        <div className="modal success-modal">
          <button className="modal-close" onClick={onClose}>
            <X size={24} />
          </button>
          
          <div className="success-icon">
            <Check size={48} color="#10b981" />
          </div>
          
          <h2>✅ Bias Correction Complete!</h2>
          
          <div className="correction-summary">
            <div className="summary-card">
              <h4>Method Applied</h4>
              <p><strong>{correctionMethod}</strong></p>
            </div>
            
            <div className="summary-card">
              <h4>Fairness Improvement</h4>
              <div className="improvement-badge">
                <TrendingUp size={16} />
                <span>0% → {(correctedData.new_fairness_score * 100).toFixed(0)}%</span>
              </div>
            </div>
            
            <div className="summary-card">
              <h4>Status</h4>
              <p className={correctedData.is_fair ? 'fair' : 'unfair'}>
                {correctedData.is_fair ? '✅ Fair Dataset' : '⚠️ Partially Corrected'}
              </p>
            </div>
          </div>
          
          <div className="correction-details">
            <h3>📊 Correction Details</h3>
            <p>{correctedData.explanation}</p>
            <p><strong>Original Score:</strong> 0%</p>
            <p><strong>New Score:</strong> {(correctedData.new_fairness_score * 100).toFixed(0)}%</p>
            <p><strong>Rows in corrected dataset:</strong> {correctedData.corrected_data_preview?.rows || 'N/A'}</p>
            
            {correctedData.corrected_data_preview?.preview_data && (
              <div className="preview-box">
                <h4>Preview of Corrected Data (first 5 rows):</h4>
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', fontSize: '12px', borderCollapse: 'collapse' }}>
                    <thead>
                      <tr>
                        {Object.keys(correctedData.corrected_data_preview.preview_data[0] || {}).map((key) => (
                          <th key={key} style={{ border: '1px solid #ddd', padding: '4px', textAlign: 'left' }}>{key}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {correctedData.corrected_data_preview.preview_data.map((row, idx) => (
                        <tr key={idx}>
                          {Object.values(row).map((val, i) => (
                            <td key={i} style={{ border: '1px solid #ddd', padding: '4px' }}>{String(val)}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
            
            {correctedData.corrected_data_preview?.recommendations && (
              <div className="preview-box">
                <h4>Recommendations:</h4>
                <ul>
                  {correctedData.corrected_data_preview.recommendations.map((rec, idx) => (
                    <li key={idx}>{rec}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
          
          <div className="modal-buttons">
            <button className="btn-secondary" onClick={onClose}>
              Close
            </button>
            <button className="btn-primary" onClick={handleDownload}>
              <FileDown size={18} />
              Download Corrected CSV
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="modal-overlay">
      <div className="modal">
        <button className="modal-close" onClick={onClose}>
          <X size={24} />
        </button>
        
        <div className="warning-icon">
          <span style={{ fontSize: '48px' }}>⚠️</span>
        </div>
        
        <h2>Bias Detected</h2>
        <p className="warning-text">
          Fairness check failed with score: <strong>{(result.fairness_score * 100).toFixed(0)}%</strong>
        </p>
        <p>Would you like to correct the data using one of these methods?</p>
        
        <div className="correction-options">
          {correctionMethods.map((method) => (
            <label key={method.value} className={`correction-option ${correctionMethod === method.value ? 'selected' : ''}`}>
              <input
                type="radio"
                value={method.value}
                checked={correctionMethod === method.value}
                onChange={(e) => setCorrectionMethod(e.target.value)}
                style={{ marginRight: '10px' }}
              />
              <div className="option-content">
                <div className="option-header">
                  <strong>{method.value}</strong>
                </div>
                <div className="option-description">{method.description}</div>
              </div>
            </label>
          ))}
        </div>
        
        <div className="modal-buttons">
          <button className="btn-secondary" onClick={onClose}>
            Cancel
          </button>
          <button 
            className="btn-primary" 
            onClick={handleCorrect}
            disabled={correcting}
          >
            {correcting ? (
              <RefreshCw className="spinning" size={20} />
            ) : (
              <Check size={20} />
            )}
            {correcting ? 'Correcting...' : 'Apply Correction'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default CorrectionModal;