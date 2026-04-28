import React from 'react';

function ResultsDashboard({ result }) {
  if (!result) return null;

  return (
    <div style={{
      background: 'rgba(255,255,255,0.15)',
      backdropFilter: 'blur(15px)',
      borderRadius: '20px',
      padding: '2rem',
      color: 'white',
      marginTop: '2rem',
      maxWidth: '900px',
      width: '100%',
    }}>
      <h2 style={{ marginBottom: '1.5rem' }}> Detailed Analysis Results</h2>
      
      {result.tables && result.tables.length > 0 && (
        <div style={{ marginBottom: '1.5rem' }}>
          <h3 style={{ marginBottom: '0.5rem' }}>Table Structure</h3>
          {result.tables.map((table, idx) => (
            <div key={idx} style={{ 
              background: 'rgba(255,255,255,0.1)', 
              padding: '15px', 
              borderRadius: '10px',
              marginBottom: '10px'
            }}>
              <p><strong>Table Name:</strong> {table.table_name || `Table ${idx + 1}`}</p>
              <p><strong>Rows:</strong> {table.rows || 'N/A'}</p>
              <p><strong>Columns:</strong> {table.columns || 'N/A'}</p>
              {table.column_names && (
                <p><strong>Column Names:</strong> {table.column_names.join(', ')}</p>
              )}
            </div>
          ))}
        </div>
      )}

      {result.sensitive_attributes && result.sensitive_attributes.length > 0 && (
        <div style={{ marginBottom: '1.5rem' }}>
          <h3 style={{ marginBottom: '0.5rem' }}> Sensitive Attributes Detected</h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
            {result.sensitive_attributes.map((attr, idx) => (
              <span key={idx} style={{
                padding: '8px 16px',
                background: 'rgba(239, 68, 68, 0.2)',
                borderRadius: '20px',
                fontSize: '0.9rem',
                border: '1px solid rgba(239, 68, 68, 0.3)',
              }}>
                {attr}
              </span>
            ))}
          </div>
        </div>
      )}

      {result.gemini_analysis && (
        <div style={{
          background: 'rgba(59, 130, 246, 0.1)',
          padding: '15px',
          borderRadius: '10px',
          border: '1px solid rgba(59, 130, 246, 0.3)',
        }}>
          <h3 style={{ marginBottom: '0.5rem' }}> AI Analysis</h3>
          <p style={{ lineHeight: '1.6' }}>{result.gemini_analysis}</p>
        </div>
      )}
    </div>
  );
}

export default ResultsDashboard;