import React from 'react';

function ExplanationPanel({ explanation }) {
  return (
    <div style={{
      background: 'rgba(255, 255, 255, 0.15)',
      backdropFilter: 'blur(10px)',
      borderRadius: '15px',
      padding: '1.5rem',
      color: 'white',
      marginTop: '2rem',
      maxWidth: '900px',
      width: '100%',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '1rem' }}>
        <span style={{ fontSize: '24px' }}></span>
        <h3 style={{ margin: 0 }}>Fairness AI</h3>
      </div>
      <div style={{ lineHeight: '1.6', whiteSpace: 'pre-wrap' }}>
        {explanation}
      </div>
    </div>
  );
}

export default ExplanationPanel;