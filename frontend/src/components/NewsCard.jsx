import React from 'react';

const NewsCard = ({ article, onSelect }) => {
  const { title, description, source, publishedAt, bias, url } = article;

  const getBiasColor = (bias) => {
    switch (bias) {
      case 'left': return 'border-l-blue-500';
      case 'right': return 'border-l-red-500';
      case 'center': return 'border-l-green-500';
      default: return 'border-l-gray-500';
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <div 
      className={`bg-white rounded-lg shadow-md border-l-4 ${getBiasColor(bias)} p-4 cursor-pointer hover:shadow-lg transition-shadow`}
      onClick={() => onSelect(article)}
    >
      <div className="flex justify-between items-start mb-2">
        <h3 className="text-lg font-semibold text-gray-800 line-clamp-2">
          {title}
        </h3>
        <span className="text-xs text-gray-500 ml-2 flex-shrink-0">
          {formatDate(publishedAt)}
        </span>
      </div>
      
      <p className="text-gray-600 text-sm mb-3 line-clamp-3">
        {description}
      </p>
      
      <div className="flex justify-between items-center">
        <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
          {source}
        </span>
        <span className={`text-xs px-2 py-1 rounded ${
          bias === 'left' ? 'bg-blue-100 text-blue-800' :
          bias === 'right' ? 'bg-red-100 text-red-800' :
          bias === 'center' ? 'bg-green-100 text-green-800' :
          'bg-gray-100 text-gray-800'
        }`}>
          {bias || 'Unknown'}
        </span>
      </div>
    </div>
  );
};

export default NewsCard;
