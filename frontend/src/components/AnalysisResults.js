import React from 'react';

function AnalysisResults({ result, onReset, onShowCorrection, onShowExplanation }) {
  return (
    <div style={{
      background: 'rgba(255, 255, 255, 0.15)',
      backdropFilter: 'blur(15px)',
      borderRadius: '20px',
      padding: '2rem',
      width: '100%',
      maxWidth: '900px',
      color: 'white',
      marginTop: '2rem',
    }}>
      <h2 style={{ textAlign: 'center', marginBottom: '1.5rem', fontSize: '2rem' }}>
        Fairness Analysis Results
      </h2>

      {/* Info Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '1rem',
        marginBottom: '2rem'
      }}>
        <div style={{ background: 'rgba(255,255,255,0.1)', padding: '15px', borderRadius: '10px' }}>
          <div style={{ fontSize: '0.8rem', opacity: 0.7 }}>Domain</div>
          <div style={{ fontSize: '1.1rem', fontWeight: 'bold' }}>{result.domain || 'N/A'}</div>
        </div>
        <div style={{ background: 'rgba(255,255,255,0.1)', padding: '15px', borderRadius: '10px' }}>
          <div style={{ fontSize: '0.8rem', opacity: 0.7 }}>File</div>
          <div style={{ fontSize: '1.1rem', fontWeight: 'bold' }}>{result.filename || 'Uploaded file'}</div>
        </div>
        <div style={{ background: 'rgba(255,255,255,0.1)', padding: '15px', borderRadius: '10px' }}>
          <div style={{ fontSize: '0.8rem', opacity: 0.7 }}>Sensitive Attributes</div>
          <div style={{ fontSize: '1.1rem', fontWeight: 'bold' }}>
            {result.sensitive_columns?.join(', ') || result.sensitive_attributes?.join(', ') || 'None'}
          </div>
        </div>
      </div>

      {/* Fairness Score Card */}
      <div style={{
        textAlign: 'center',
        padding: '2rem',
        margin: '1.5rem 0',
        background: result.is_fair ? 'rgba(52, 211, 153, 0.2)' : 'rgba(239, 68, 68, 0.2)',
        border: `2px solid ${result.is_fair ? 'rgba(52, 211, 153, 0.5)' : 'rgba(239, 68, 68, 0.5)'}`,
        borderRadius: '15px',
      }}>
        <p style={{ fontSize: '1.3rem', marginBottom: '1rem' }}>
          {result.is_fair ? ' Dataset is Fair' : '⚠️ Dataset Shows Bias'}
        </p>
        <div style={{
          fontSize: '4rem',
          fontWeight: 'bold',
          color: result.is_fair ? '#34D399' : '#EF4444',
          textShadow: '2px 2px 4px rgba(0,0,0,0.2)',
        }}>
          {(result.fairness_score * 100).toFixed(1)}%
        </div>
        <p style={{ marginTop: '0.5rem', opacity: 0.8, fontSize: '1.1rem' }}>Fairness Score</p>
      </div>

      {/* Metrics */}
      {result.metrics && Object.keys(result.metrics).length > 0 && (
        <div style={{ margin: '2rem 0' }}>
          <h3 style={{ marginBottom: '1rem' }}>Detailed Metrics</h3>
          {Object.entries(result.metrics).map(([attr, data]) => (
            <div key={attr} style={{ margin: '1rem 0' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <span style={{ fontWeight: '600' }}>{attr}</span>
                <span>{typeof data === 'object' ? (data.score * 100).toFixed(1) : (data * 100).toFixed(1)}%</span>
              </div>
              <div style={{
                height: '10px',
                background: 'rgba(255, 255, 255, 0.2)',
                borderRadius: '5px',
                overflow: 'hidden'
              }}>
                <div style={{
                  height: '100%',
                  width: `${(typeof data === 'object' ? data.score : data) * 100}%`,
                  background: (typeof data === 'object' ? data.is_fair : data >= 0.8) ? 
                    'linear-gradient(90deg, #34D399, #059669)' : 
                    'linear-gradient(90deg, #F59E0B, #EF4444)',
                  borderRadius: '5px',
                  transition: 'width 0.5s ease'
                }} />
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Action Buttons */}
      <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', flexWrap: 'wrap', marginTop: '2rem' }}>
        {!result.is_fair && onShowCorrection && (
          <button
            onClick={onShowCorrection}
            style={buttonStyle('#EF4444')}
          >
            🔧 Correct Bias
          </button>
        )}
        {result.explanation && onShowExplanation && (
          <button
            onClick={onShowExplanation}
            style={buttonStyle('#3B82F6')}
          >
            View Explanation
          </button>
        )}
        <button
          onClick={onReset}
          style={buttonStyle('#667eea')}
        >
          📤 New Analysis
        </button>
      </div>
    </div>
  );
}

const buttonStyle = (color) => ({
  background: `linear-gradient(135deg, ${color}, ${color}dd)`,
  color: 'white',
  border: 'none',
  padding: '14px 28px',
  borderRadius: '12px',
  fontSize: '1.1rem',
  cursor: 'pointer',
  boxShadow: '0 4px 15px rgba(0,0,0,0.2)',
  transition: 'transform 0.2s',
});

export default AnalysisResults;