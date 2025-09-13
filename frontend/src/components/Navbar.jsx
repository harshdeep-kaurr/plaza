import React from 'react';

const Navbar = ({ onNavigate, currentPage }) => {
  return (
    <nav className="bg-white shadow-lg border-b">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <h1 className="text-2xl font-bold text-purple-800">
              PLAZA
            </h1>
          </div>
          
          <div className="flex space-x-4">
            <button
              onClick={() => onNavigate('home')}
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                currentPage === 'home'
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              Home
            </button>
            <button
              onClick={() => onNavigate('chat')}
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                currentPage === 'chat'
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              Chat
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
