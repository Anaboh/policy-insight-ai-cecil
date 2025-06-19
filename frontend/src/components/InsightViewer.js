import React from 'react';

const InsightViewer = ({ insights, onReset }) => {
  return (
    <div className="insights-container">
      <div className="header-row">
        <h2>Analysis for: {insights.filename}</h2>
        <button onClick={onReset} className="reset-btn">Analyze Another</button>
      </div>

      <div className="card">
        <div className="summary-content">
          {insights.summary.split('###').map((section, index) => (
            section.trim() ? (
              <div key={index}>
                <h3>{section.split('\n')[0].trim()}</h3>
                <div className="section-content">
                  {section.split('\n').slice(1).join('\n').trim()}
                </div>
              </div>
            ) : null
          ))}
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
