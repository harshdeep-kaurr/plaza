import React, { useState } from 'react';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Chat from './pages/Chat';

function App() {
  const [currentPage, setCurrentPage] = useState('home');
  const [selectedArticle, setSelectedArticle] = useState(null);
  const [selectedTopic, setSelectedTopic] = useState(null);

  const handleNavigate = (page, data = null) => {
    setCurrentPage(page);
    
    if (data) {
      if (data.article) setSelectedArticle(data.article);
      if (data.topic) setSelectedTopic(data.topic);
    }
  };

  const renderPage = () => {
    switch (currentPage) {
      case 'chat':
        return (
          <Chat
            selectedArticle={selectedArticle}
            selectedTopic={selectedTopic}
            onNavigate={handleNavigate}
          />
        );
      case 'home':
      default:
        return <Home onNavigate={handleNavigate} />;
    }
  };

  return (
    <div className="App">
      <Navbar 
        currentPage={currentPage} 
        onNavigate={handleNavigate} 
      />
      {renderPage()}
    </div>
  );
}

export default App;
