import React from 'react';

export default function InsightsView({ insights, onReset }) {
  // Parse the AI response
  const parseInsights = (text) => {
    const result = {
      summary: '',
      impacts: '',
      urgency: '',
      steps: ''
    };
    
    try {
      // Executive Summary
      const summaryMatch = text.match(/## Executive Summary\n([\s\S]*?)(?=## |$)/i);
      if (summaryMatch) result.summary = summaryMatch[1].trim();
      
      // Key Impacts
      const impactsMatch = text.match(/## Key Impacts\n([\s\S]*?)(?=## |$)/i);
      if (impactsMatch) result.impacts = impactsMatch[1].trim();
      
      // Urgency Assessment
      const urgencyMatch = text.match(/## Urgency Assessment\n([\s\S]*?)(?=## |$)/i);
      if (urgencyMatch) result.urgency = urgencyMatch[1].trim();
      
      // Recommended Actions
      const stepsMatch = text.match(/## Recommended Actions\n([\s\S]*)/i);
      if (stepsMatch) result.steps = stepsMatch[1].trim();
    } catch (e) {
      console.error("Error parsing insights:", e);
    }
    
    return result;
  };

  const sections = parseInsights(insights);

  return (
    <div className="insights-container">
      <div className="insights-header">
        <h2>Policy Brief</h2>
        <button onClick={onReset} className="reset-button">
          Analyze New Document
        </button>
      </div>
      
      {sections.summary ? (
        <div className="insight-section">
          <h3>Executive Summary</h3>
          <p>{sections.summary}</p>
        </div>
      ) : null}
      
      {sections.impacts ? (
        <div className="insight-section">
          <h3>Key Impacts</h3>
          <pre>{sections.impacts}</pre>
        </div>
      ) : null}
      
      {sections.urgency ? (
        <div className="insight-section">
          <h3>Urgency Assessment</h3>
          <p>{sections.urgency}</p>
        </div>
      ) : null}
      
      {sections.steps ? (
        <div className="insight-section">
          <h3>Recommended Actions</h3>
          <pre>{sections.steps}</pre>
        </div>
      ) : (
        <div className="insight-section">
          <h3>Full Response</h3>
          <pre>{insights}</pre>
        </div>
      )}
    </div>
  );
}
