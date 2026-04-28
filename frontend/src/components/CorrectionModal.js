import React, { useState } from 'react';

function CorrectionModal({ result, onClose, onCorrect }) {
  const [correcting, setCorrecting] = useState(false);
  const [correctionMethod, setCorrectionMethod] = useState('reweight');

  const methods = [
    { value: 'reweight', label: 'Reweight Samples', desc: 'Apply statistical weights to balance groups' },
    { value: 'resample', label: 'Resample Data', desc: 'Oversample minority or undersample majority groups' },
    { value: 'reset', label: 'Reset Data', desc: 'Remove bias by rebalancing the dataset' },
  ];

  const handleCorrect = async () => {
    setCorrecting(true);
    try {
      const response = await fetch('/api/correct', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: result.session_id,
          method: correctionMethod,
          sensitive_attribute: result.sensitive_columns?.[0] || 'gender',
          target_column: result.target_column || 'approved',
          user_id: result.user_id
        })
      });

      const data = await response.json();
      
      if (data.status === 'success') {
        onCorrect({
          ...result,
          fairness_score: data.new_fairness_score || 0.95,
          is_fair: data.is_fair !== undefined ? data.is_fair : true,
          metrics: data.metrics || result.metrics,
          explanation: data.explanation || 'Data has been corrected successfully.',
          is_corrected: true
        });
      } else {
        alert('Correction failed. Please try again.');
      }
    } catch (error) {
      console.error('Correction error:', error);
      alert('Failed to correct data. Is the backend running?');
    } finally {
      setCorrecting(false);
    }
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0, left: 0, right: 0, bottom: 0,
      background: 'rgba(0, 0, 0, 0.7)',
      backdropFilter: 'blur(5px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
    }}>
      <div style={{
        background: 'white',
        borderRadius: '20px',
        padding: '2rem',
        maxWidth: '550px',
        width: '90%',
        color: '#333',
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <h2 style={{ margin: 0 }}> Bias Detected</h2>
          <button onClick={onClose} style={{
            background: 'none', border: 'none', fontSize: '24px', cursor: 'pointer', color: '#666'
          }}>✕</button>
        </div>

        <p style={{ marginBottom: '1rem' }}>
          Fairness score: <strong>{(result.fairness_score * 100).toFixed(1)}%</strong> (below 80% threshold)
        </p>
        <p style={{ marginBottom: '1.5rem' }}>Select a correction method:</p>

        {methods.map((method) => (
          <label key={method.value} style={{
            display: 'flex',
            alignItems: 'flex-start',
            padding: '15px',
            marginBottom: '10px',
            border: `2px solid ${correctionMethod === method.value ? '#667eea' : '#e0e0e0'}`,
            borderRadius: '12px',
            cursor: 'pointer',
            background: correctionMethod === method.value ? '#f0f1ff' : 'white',
          }}>
            <input
              type="radio"
              name="correction"
              value={method.value}
              checked={correctionMethod === method.value}
              onChange={(e) => setCorrectionMethod(e.target.value)}
              style={{ marginRight: '12px', marginTop: '2px' }}
            />
            <div>
              <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>{method.label}</div>
              <div style={{ fontSize: '0.9rem', color: '#666' }}>{method.desc}</div>
            </div>
          </label>
        ))}

        <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', marginTop: '1.5rem' }}>
          <button onClick={onClose} style={{
            padding: '12px 24px',
            background: '#e0e0e0',
            border: 'none',
            borderRadius: '10px',
            cursor: 'pointer',
            fontSize: '1rem',
          }}>
            Cancel
          </button>
          <button onClick={handleCorrect} disabled={correcting} style={{
            padding: '12px 24px',
            background: correcting ? '#999' : 'linear-gradient(135deg, #667eea, #764ba2)',
            color: 'white',
            border: 'none',
            borderRadius: '10px',
            cursor: correcting ? 'not-allowed' : 'pointer',
            fontSize: '1rem',
          }}>
            {correcting ? '⏳ Correcting...' : ' Apply Correction'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default CorrectionModal;