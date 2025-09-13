import React, { useState, useEffect } from 'react';
import ChatBubble from '../components/ChatBubble';

const Chat = ({ selectedArticle, selectedTopic, onNavigate }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [persona, setPersona] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (selectedArticle && selectedTopic) {
      // Load conversation history or start new conversation
      loadConversation();
    }
  }, [selectedArticle, selectedTopic]);

  const loadConversation = async () => {
    try {
      const response = await fetch(`/api/conversations?topic=${encodeURIComponent(selectedTopic.name)}&article=${encodeURIComponent(selectedArticle.id)}`);
      const data = await response.json();
      
      if (data.conversation) {
        setMessages(data.conversation.messages || []);
        setPersona(data.conversation.persona);
      } else {
        // Start new conversation
        await startNewConversation();
      }
    } catch (error) {
      console.error('Error loading conversation:', error);
      await startNewConversation();
    }
  };

  const startNewConversation = async () => {
    try {
      const response = await fetch('/api/conversations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topic: selectedTopic.name,
          article: selectedArticle,
        }),
      });
      
      const data = await response.json();
      setPersona(data.persona);
      
      // Add initial message from persona
      setMessages([{
        id: 1,
        text: data.initialMessage,
        isUser: false,
        persona: data.persona,
      }]);
    } catch (error) {
      console.error('Error starting conversation:', error);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

    const userMessage = {
      id: Date.now(),
      text: inputMessage,
      isUser: true,
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setLoading(true);

    try {
      const response = await fetch('/api/conversations/message', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topic: selectedTopic.name,
          article: selectedArticle,
          message: inputMessage,
          persona: persona,
        }),
      });

      const data = await response.json();
      
      const botMessage = {
        id: Date.now() + 1,
        text: data.response,
        isUser: false,
        persona: persona,
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!selectedArticle || !selectedTopic) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">
            No conversation selected
          </h2>
          <button
            onClick={() => onNavigate('home')}
            className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600"
          >
            Go to Home
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Chat Header */}
      <div className="bg-white shadow-sm border-b p-4">
        <div className="max-w-4xl mx-auto">
          <button
            onClick={() => onNavigate('home')}
            className="text-blue-500 hover:text-blue-700 mb-2"
          >
            ← Back to Home
          </button>
          <h1 className="text-xl font-semibold text-gray-800">
            Chatting about: {selectedTopic.name}
          </h1>
          <p className="text-sm text-gray-600">
            Article: {selectedArticle.title}
          </p>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="max-w-4xl mx-auto">
          {messages.map((message) => (
            <ChatBubble
              key={message.id}
              message={message.text}
              isUser={message.isUser}
              persona={message.persona}
            />
          ))}
          
          {loading && (
            <div className="flex justify-start mb-4">
              <div className="bg-gray-100 rounded-lg px-4 py-2">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Input */}
      <div className="bg-white border-t p-4">
        <div className="max-w-4xl mx-auto">
          <form onSubmit={handleSendMessage} className="flex space-x-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Type your message..."
              className="flex-1 border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !inputMessage.trim()}
              className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Send
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Chat;
