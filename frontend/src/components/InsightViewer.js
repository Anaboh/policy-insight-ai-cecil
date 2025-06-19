import React from 'react';

const InsightViewer = ({ insights }) => {
  return (
    <div className="insights-container">
      <h3>Executive Summary</h3>
      <div className="card">
        <ul className="key-points">
          {insights.key_points?.map((point, i) => (
            <li key={i}>{point}</li>
          ))}
        </ul>
        
        <h4>Detailed Analysis</h4>
        <div className="detailed-summary">
          {insights.summary}
        </div>
      </div>
      
      <div className="actions">
        <button onClick={() => navigator.clipboard.writeText(insights.summary)}>
          Copy to Clipboard
        </button>
      </div>
    </div>
  );
};

export default InsightViewer;
