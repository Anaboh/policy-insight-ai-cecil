import React from 'react';

export default function InsightsView({ insights, onReset }) {
  // Parse the AI response
  const sections = {
    summary: insights.match(/# Executive Summary\n([\s\S]*?)(?=# |$)/)?.[1]?.trim(),
    impacts: insights.match(/# Key Impacts\n([\s\S]*?)(?=# |$)/)?.[1]?.trim(),
    urgency: insights.match(/# Urgency\n([\s\S]*?)(?=# |$)/)?.[1]?.trim(),
    steps: insights.match(/# Recommended Next Steps\n([\s\S]*?)(?=# |$)/)?.[1]?.trim()
  };

  return (
    <div className="insights-container">
      <div className="insights-header">
        <h2>Policy Brief</h2>
        <button onClick={onReset} className="reset-button">
          Analyze New Document
        </button>
      </div>
      
      <div className="insight-section">
        <h3>Executive Summary</h3>
        <p>{sections.summary || 'Not available'}</p>
      </div>
      
      <div className="insight-section">
        <h3>Key Impacts</h3>
        <pre>{sections.impacts || 'Not available'}</pre>
      </div>
      
      <div className="insight-section">
        <h3>Urgency Assessment</h3>
        <p>{sections.urgency || 'Not available'}</p>
      </div>
      
      <div className="insight-section">
        <h3>Recommended Actions</h3>
        <pre>{sections.steps || 'Not available'}</pre>
      </div>
    </div>
  );
}
