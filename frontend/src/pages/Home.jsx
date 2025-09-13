import React, { useState, useEffect } from 'react';
import NewsCard from '../components/NewsCard';

const Home = ({ onNavigate }) => {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const sampleArticles = [
      {
        id: 1,
        title: "Breaking: Major Tech Innovation",
        summary: "Revolutionary technology breakthrough changes everything",
        topic: "Technology"
      },
      {
        id: 2,
        title: "Global Economic Update",
        summary: "Latest developments in international markets",
        topic: "Economy"
      },
      {
        id: 3,
        title: "Climate Action Progress",
        summary: "New environmental initiatives show promise",
        topic: "Environment"
      },
      {
        id: 4,
        title: "Healthcare Breakthrough",
        summary: "Medical research achieves significant milestone",
        topic: "Health"
      }
    ];
    setArticles(sampleArticles);
  }, []);

  const handleArticleSelect = (article) => {
    onNavigate('chat', { article });
  };

  const handleMessageClick = (e, article) => {
    e.stopPropagation();
    onNavigate('chat', { article });
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="max-w-6xl mx-auto px-6 py-12">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-amber-800">TODAY'S TOP NEWS</h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {articles.map((article, index) => (
            <div
              key={article.id}
              className="bg-amber-100 h-48 rounded-lg cursor-pointer hover:bg-amber-200 transition-colors duration-200 flex items-center justify-center p-4 relative"
            >
              {/* Message Icon */}
              <button
                onClick={(e) => handleMessageClick(e, article)}
                className="absolute bottom-3 right-3 p-2 bg-purple-600 hover:bg-purple-700 text-white rounded-full transition-colors duration-200"
                title="Join group chat"
              >
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clipRule="evenodd" />
                </svg>
              </button>
              
              <div className="text-center">
                <h3 className="font-semibold text-amber-800 text-lg mb-2">{article.title}</h3>
                <p className="text-amber-700 text-sm">{article.summary}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Home;
