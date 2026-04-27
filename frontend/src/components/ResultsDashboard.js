import React from 'react';

const ResultsDashboard = ({ result }) => {
  if (!result) return null;

  return (
    <div className="results-dashboard" style={{ 
      marginTop: '20px', 
      padding: '20px', 
      borderTop: '1px solid #ddd',
      backgroundColor: '#fff',
      borderRadius: '8px'
    }}>
      <h2 style={{ color: '#333', marginBottom: '20px' }}>Analysis Results</h2>
      
      {/* Fairness Score */}
      <div className="fairness-score" style={{ marginBottom: '20px' }}>
        <h3>Fairness Score: {(result.fairness_score * 100).toFixed(1)}%</h3>
        <div style={{
          width: '100%',
          height: '20px',
          backgroundColor: '#f0f0f0',
          borderRadius: '10px',
          overflow: 'hidden'
        }}>
          <div style={{
            width: `${result.fairness_score * 100}%`,
            height: '100%',
            backgroundColor: result.is_fair ? '#4caf50' : '#ff9800',
            transition: 'width 0.5s ease'
          }} />
        </div>
        <p style={{ color: result.is_fair ? '#4caf50' : '#ff9800', marginTop: '10px', fontWeight: 'bold' }}>
          {result.is_fair ? '✅ Dataset appears fair' : '⚠️ Potential fairness issues detected'}
        </p>
      </div>

      {/* Data Information */}
      <div className="data-info" style={{ marginBottom: '20px' }}>
        <h3 style={{ color: '#555', marginBottom: '10px' }}>Data Summary</h3>
        <p><strong>File:</strong> {result.filename}</p>
        <p><strong>Domain:</strong> {result.domain}</p>
        {result.tables && result.tables.length > 0 && (
          <>
            <p><strong>Rows:</strong> {result.tables[0].rows}</p>
            <p><strong>Columns:</strong> {result.tables[0].columns}</p>
          </>
        )}
      </div>

      {/* Column Information */}
      {result.tables && result.tables.length > 0 && result.tables[0].column_names && (
        <div className="columns-info" style={{ marginBottom: '20px' }}>
          <h3 style={{ color: '#555', marginBottom: '10px' }}>Columns</h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
            {result.tables[0].column_names.map((col, idx) => (
              <span key={idx} style={{
                padding: '5px 10px',
                backgroundColor: result.numeric_columns?.includes(col) ? '#e3f2fd' : '#f3e5f5',
                borderRadius: '5px',
                fontSize: '12px',
                border: '1px solid #ddd'
              }}>
                {col}
                {result.numeric_columns?.includes(col) && ' (numeric)'}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Metrics Table */}
      {result.metrics && (
        <div className="metrics" style={{ marginBottom: '20px' }}>
          <h3 style={{ color: '#555', marginBottom: '10px' }}>Fairness Metrics</h3>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ backgroundColor: '#f5f5f5', borderBottom: '2px solid #ddd' }}>
                <th style={{ padding: '10px', textAlign: 'left' }}>Metric</th>
                <th style={{ padding: '10px', textAlign: 'left' }}>Value</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(result.metrics).map(([key, value]) => (
                <tr key={key} style={{ borderBottom: '1px solid #eee' }}>
                  <td style={{ padding: '8px', fontWeight: 'bold' }}>
                    {key.replace(/_/g, ' ').toUpperCase()}
                  </td>
                  <td style={{ padding: '8px' }}>
                    {(value * 100).toFixed(1)}%
                    <div style={{
                      width: '100%',
                      height: '5px',
                      backgroundColor: '#e0e0e0',
                      borderRadius: '3px',
                      marginTop: '5px',
                      overflow: 'hidden'
                    }}>
                      <div style={{
                        width: `${value * 100}%`,
                        height: '100%',
                        backgroundColor: value >= 0.8 ? '#4caf50' : value >= 0.6 ? '#ff9800' : '#f44336',
                        borderRadius: '3px'
                      }} />
                    </div>
                   </td>
                 </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Sensitive Attributes */}
      {result.sensitive_attributes && result.sensitive_attributes.length > 0 && (
        <div className="sensitive-attrs" style={{ marginBottom: '20px' }}>
          <h3 style={{ color: '#555', marginBottom: '10px' }}>Sensitive Attributes</h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
            {result.sensitive_attributes.map((attr, idx) => (
              <span key={idx} style={{
                padding: '5px 10px',
                backgroundColor: '#ffebee',
                borderRadius: '5px',
                fontSize: '12px',
                border: '1px solid #ef9a9a',
                color: '#c62828'
              }}>
                {attr}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Explanation */}
      {result.explanation && (
        <div className="explanation" style={{
          padding: '15px',
          backgroundColor: '#f9f9f9',
          borderRadius: '8px',
          marginBottom: '20px',
          borderLeft: '4px solid #3b82f6'
        }}>
          <h3 style={{ color: '#555', marginBottom: '10px' }}>📝 Explanation</h3>
          <p style={{ lineHeight: '1.6', color: '#666' }}>{result.explanation}</p>
        </div>
      )}

      {/* Gemini Analysis */}
      {result.gemini_analysis && (
        <div className="gemini-analysis" style={{
          padding: '15px',
          backgroundColor: '#e8f4f8',
          borderRadius: '8px',
          marginBottom: '20px',
          borderLeft: '4px solid #10b981'
        }}>
          <h3 style={{ color: '#555', marginBottom: '10px' }}>🤖 Gemini AI Analysis</h3>
          <p style={{ lineHeight: '1.6', color: '#666' }}>{result.gemini_analysis}</p>
        </div>
      )}

      {/* RAG Insights */}
      {result.rag_insights && (
        <div className="rag-insights" style={{
          padding: '15px',
          backgroundColor: '#fef3e8',
          borderRadius: '8px',
          borderLeft: '4px solid #ff9800'
        }}>
          <h3 style={{ color: '#555', marginBottom: '10px' }}>📚 RAG Insights</h3>
          <p><strong>Similar Sessions Found:</strong> {result.rag_insights.similar_sessions_found}</p>
          <p><strong>Bias Patterns Found:</strong> {result.rag_insights.bias_patterns_found}</p>
          {result.rag_insights.historical_context && result.rag_insights.historical_context.length > 0 && (
            <details>
              <summary style={{ cursor: 'pointer', color: '#3b82f6', marginTop: '10px' }}>
                View Historical Context
              </summary>
              <pre style={{ 
                marginTop: '10px', 
                padding: '10px', 
                backgroundColor: '#fff',
                borderRadius: '5px',
                overflow: 'auto',
                fontSize: '12px'
              }}>
                {JSON.stringify(result.rag_insights.historical_context, null, 2)}
              </pre>
            </details>
          )}
        </div>
      )}
    </div>
  );
};

export default ResultsDashboard;