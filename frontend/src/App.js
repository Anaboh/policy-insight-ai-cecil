import React, { useState } from 'react';
import Uploader from './components/Uploader';
import InsightsView from './components/InsightsView';
import './index.css';

function App() {
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleUpload = async (file) => {
    setLoading(true);
    setError('');
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const backendUrl = process.env.REACT_APP_API_URL || '/analyze';
      const response = await fetch(backendUrl, {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) throw new Error('Analysis failed');
      
      const data = await response.json();
      setInsights(data.insights);
    } catch (err) {
      setError(err.message || 'Error processing document');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>PolicyInsight AI</h1>
        <p>Transform PDFs into executive briefings</p>
      </header>
      
      <main className="app-main">
        {!insights ? (
          <Uploader onUpload={handleUpload} loading={loading} />
        ) : (
          <InsightsView insights={insights} 
                        onReset={() => setInsights(null)} />
        )}
        
        {error && <div className="error-message">{error}</div>}
      </main>
      
      <footer className="app-footer">
        <p>Powered by DeepSeek AI • For decision makers</p>
      </footer>
    </div>
  );
}

export default App;
