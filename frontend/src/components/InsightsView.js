import React from 'react';

export default function InsightsView({ insights, onReset }) {
  // Parse the AI response
  const sections = {
    summary: insights.match(/Executive Summary([\s\S]*?)(?=Key Impacts|$)/i)?.[1]?.trim(),
    impacts: insights.match(/Key Impacts([\s\S]*?)(?=Urgency|$)/i)?.[1]?.trim(),
    urgency: insights.match(/Urgency([\s\S]*?)(?=Recommended|$)/i)?.[1]?.trim(),
    steps: insights.match(/Recommended Next Steps([\s\S]*)/i)?.[1]?.trim()
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
        <p>{sections.summary || insights}</p>
      </div>
      
      {sections.impacts && (
        <div className="insight-section">
          <h3>Key Impacts</h3>
          <pre>{sections.impacts}</pre>
        </div>
      )}
      
      {sections.urgency && (
        <div className="insight-section">
          <h3>Urgency Assessment</h3>
          <p>{sections.urgency}</p>
        </div>
      )}
      
      {sections.steps && (
        <div className="insight-section">
          <h3>Recommended Actions</h3>
          <pre>{sections.steps}</pre>
        </div>
      )}
    </div>
  );
}
