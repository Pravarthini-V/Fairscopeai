import React, { useState } from 'react';
import ThreeBackground from './components/ThreeBackground';
import FileUpload from './components/FileUpload';
import AnalysisResults from './components/AnalysisResults';
import ResultsDashboard from './components/ResultsDashboard';
import CorrectionModal from './components/CorrectionModal';
import ExplanationPanel from './components/ExplanationPanel';

function App() {
  const [analysisResult, setAnalysisResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showCorrection, setShowCorrection] = useState(false);
  const [showExplanation, setShowExplanation] = useState(false);

  const handleFileUpload = async (file) => {
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/analyze', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }
      
      const result = await response.json();
      setAnalysisResult(result);
    } catch (error) {
      console.error('Analysis failed:', error);
      alert('Analysis failed. Please check if the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleCorrect = (correctedResult) => {
    setAnalysisResult(correctedResult);
    setShowCorrection(false);
  };

  const resetAnalysis = () => {
    setAnalysisResult(null);
    setShowCorrection(false);
    setShowExplanation(false);
  };

  return (
    <div style={{ 
      position: 'relative', 
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    }}>
      {/* 3D Background */}
      <ThreeBackground />
      
      {/* Main Content */}
      <div style={{
        position: 'relative',
        zIndex: 1,
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        padding: '2rem',
      }}>
        {/* Header */}
        <h1 style={{
          color: 'white',
          fontSize: '2.5rem',
          textAlign: 'center',
          marginBottom: '2rem',
          textShadow: '2px 2px 4px rgba(0,0,0,0.3)',
        }}>
          🎯 AI Fairness Detection System
        </h1>

        {!analysisResult ? (
          /* Upload Section */
          <FileUpload onUpload={handleFileUpload} loading={loading} />
        ) : (
          /* Results Section */
          <div style={{ width: '100%', maxWidth: '1200px' }}>
            <AnalysisResults
              result={analysisResult}
              onReset={resetAnalysis}
              onShowCorrection={() => setShowCorrection(true)}
              onShowExplanation={() => setShowExplanation(true)}
            />
            
            {/* Results Dashboard with detailed metrics */}
            <div style={{ marginTop: '2rem' }}>
              <ResultsDashboard result={analysisResult} />
            </div>
            
            {/* Explanation Panel */}
            {showExplanation && analysisResult.explanation && (
              <div style={{ marginTop: '2rem' }}>
                <ExplanationPanel explanation={analysisResult.explanation} />
              </div>
            )}
          </div>
        )}
        
        {/* Correction Modal */}
        {showCorrection && analysisResult && (
          <CorrectionModal
            result={analysisResult}
            onClose={() => setShowCorrection(false)}
            onCorrect={handleCorrect}
          />
        )}
      </div>
    </div>
  );
}

export default App;