import React, { useState } from 'react';
import FileUpload from './components/FileUpload';
import InsightViewer from './components/InsightViewer';
import './App.css';

function App() {
  const [insights, setInsights] = useState(null);

  const handleAnalysisComplete = (data) => {
    setInsights(data);
  };

  const handleReset = () => {
    setInsights(null);
  };

  return (
    <div className="App">
      <header>
        <h1>Policy Insight Agent</h1>
        <p>AI-powered PDF analysis for policymakers</p>
      </header>

      <main>
        {!insights ? (
          <FileUpload onAnalysisComplete={handleAnalysisComplete} />
        ) : (
          <InsightViewer insights={insights} onReset={handleReset} />
        )}
      </main>

      <footer>
        <p>Powered by DeepSeek AI</p>
      </footer>
    </div>
  );
}

export default App;
