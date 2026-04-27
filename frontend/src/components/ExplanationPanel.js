
import React from 'react';
import { Info } from 'lucide-react';

const ExplanationPanel = ({ explanation }) => {
  return (
    <div className="explanation-panel">
      <div className="explanation-header">
        <Info size={20} />
        <h3>Explanation & Recommendations</h3>
      </div>
      <div className="explanation-content">
        <pre>{explanation}</pre>
      </div>
    </div>
  );
};

export default ExplanationPanel;