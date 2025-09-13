import React from 'react';

const ChatBubble = ({ message, isUser = false, persona = null }) => {
  if (isUser) {
    return (
      <div className="flex justify-end mb-4">
        <div className="bg-blue-500 text-white rounded-lg px-4 py-2 max-w-xs lg:max-w-md">
          <p className="text-sm">{message}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start mb-4">
      <div className="flex items-start space-x-2">
        {persona && (
          <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center text-sm">
            {persona.avatar}
          </div>
        )}
        <div className="bg-gray-100 rounded-lg px-4 py-2 max-w-xs lg:max-w-md">
          {persona && (
            <div className="text-xs text-gray-600 mb-1 font-medium">
              {persona.name}
            </div>
          )}
          <p className="text-sm text-gray-800">{message}</p>
        </div>
      </div>
    </div>
  );
};

export default ChatBubble;
