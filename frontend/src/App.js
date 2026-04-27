import React, { useState } from 'react';
import FileUploader from './components/FileUploader';
import ResultsDashboard from './components/ResultsDashboard';
import CorrectionModal from './components/CorrectionModal';
import ExplanationPanel from './components/ExplanationPanel';
import './App.css';

function App() {
  const [analysisResult, setAnalysisResult] = useState(null);
  const [showCorrection, setShowCorrection] = useState(false);
  const [loading, setLoading] = useState(false);

  return (
    <div className="app-container">
      <div className="content">
        <header className="header">
          <h1 className="title">FairScope</h1>
          <p className="subtitle">Dynamic Fairness Detection & Correction System</p>
        </header>

        <div className="main-card">
          <FileUploader 
            onAnalysisStart={() => setLoading(true)}
            onAnalysisComplete={(result) => {
              setAnalysisResult(result);
              setLoading(false);
              // Show correction modal ONLY if dataset is unfair
              if (!result.is_fair) {
                setShowCorrection(true);
              }
            }}
          />

          {loading && (
            <div className="loading">
              <div className="spinner"></div>
              <p>Analyzing fairness metrics...</p>
            </div>
          )}

          {analysisResult && !showCorrection && (
            <>
              <ResultsDashboard result={analysisResult} />
              <ExplanationPanel explanation={analysisResult.explanation} />
            </>
          )}
        </div>

        {showCorrection && analysisResult && (
          <CorrectionModal
            result={analysisResult}
            onClose={() => setShowCorrection(false)}
            onCorrect={(correctedData) => {
              setAnalysisResult(correctedData);
              setShowCorrection(false);
            }}
          />
        )}
      </div>
    </div>
  );
}

export default App;