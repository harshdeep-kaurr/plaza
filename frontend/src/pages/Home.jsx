import React, { useState, useEffect } from 'react';
import NewsCard from '../components/NewsCard';

const Home = ({ onNavigate }) => {
  const [topics, setTopics] = useState([]);
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Load topics from data file
    fetch('/data/topics.json')
      .then(response => response.json())
      .then(data => setTopics(data))
      .catch(error => console.error('Error loading topics:', error));
  }, []);

  const handleTopicSelect = async (topic) => {
    setSelectedTopic(topic);
    setLoading(true);
    
    try {
      // Fetch articles for selected topic
      const response = await fetch(`/api/articles?topic=${encodeURIComponent(topic.name)}`);
      const data = await response.json();
      setArticles(data.articles || []);
    } catch (error) {
      console.error('Error fetching articles:', error);
      setArticles([]);
    } finally {
      setLoading(false);
    }
  };

  const handleArticleSelect = (article) => {
    // Navigate to chat page with selected article
    onNavigate('chat', { article, topic: selectedTopic });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          Explore News Topics
        </h1>
        
        {/* Topics Grid */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Topics</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {topics.map((topic, index) => (
              <div
                key={index}
                onClick={() => handleTopicSelect(topic)}
                className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                  selectedTopic?.name === topic.name
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300 bg-white'
                }`}
              >
                <h3 className="font-semibold text-gray-800">{topic.name}</h3>
                <p className="text-sm text-gray-600 mt-1">{topic.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Articles Section */}
        {selectedTopic && (
          <div>
            <h2 className="text-xl font-semibold text-gray-800 mb-4">
              Articles about {selectedTopic.name}
            </h2>
            
            {loading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
                <p className="text-gray-600 mt-2">Loading articles...</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {articles.map((article, index) => (
                  <NewsCard
                    key={index}
                    article={article}
                    onSelect={handleArticleSelect}
                  />
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Home;
