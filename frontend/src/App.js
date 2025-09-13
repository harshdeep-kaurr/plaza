import React, { useState, useRef, useEffect } from "react";
import { Routes, Route, Link, useParams, useNavigate } from "react-router-dom";
import topics from "./data/topics";

// Backend API base URL
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001';

function Home() {
  return (
    <main className="max-w-6xl mx-auto px-4 py-10">
      {/* Header */}
      <header className="mb-8">
        <h1 className="text-5xl leading-tight tracking-tight font-black flex items-center gap-4">
          <svg 
            width="48" 
            height="48" 
            viewBox="0 0 24 24" 
            fill="none" 
            xmlns="http://www.w3.org/2000/svg"
            className="text-[color:var(--ink)]"
          >
            <rect x="2" y="2" width="20" height="20" rx="2" stroke="currentColor" strokeWidth="2" fill="none"/>
            <rect x="6" y="6" width="4" height="4" rx="1" fill="currentColor"/>
            <rect x="14" y="6" width="4" height="4" rx="1" fill="currentColor"/>
            <rect x="6" y="14" width="4" height="4" rx="1" fill="currentColor"/>
            <rect x="14" y="14" width="4" height="4" rx="1" fill="currentColor"/>
            <circle cx="10" cy="10" r="1" fill="currentColor"/>
            <circle cx="14" cy="10" r="1" fill="currentColor"/>
            <circle cx="10" cy="14" r="1" fill="currentColor"/>
            <circle cx="14" cy="14" r="1" fill="currentColor"/>
          </svg>
          PLAZA
        </h1>
        <h2 className="text-2xl font-bold italic text-[color:var(--ink-light)] mt-2">
          Where headlines become conversations.
        </h2>
        <div className="hr my-6"></div>
        <p className="text-lg text-[color:var(--ink-light)] max-w-3xl">
          Jump into the conversation. Each topic has its plaza.
        </p>
      </header>

      {/* Tiles grid */}
      <section className="grid md:grid-cols-3 sm:grid-cols-2 grid-cols-1 gap-8">
        {topics.map((t) => (
          <Link
            to={`/plaza/${t.id}`}
            key={t.id}
            className="tile group block"
          >
            <article className="bg-white shadow-sm ring-1 ring-[color:var(--rule)] h-96 flex flex-col">
              <div className="h-64 overflow-hidden">
                <img
                  src={t.image}
                  alt={t.title}
                  className="w-full h-full object-cover"
                  loading="lazy"
                />
              </div>
              <div className="p-4 flex flex-col justify-center">
                <h2 className="font-black text-2xl leading-snug mb-2">
                  {t.title}
                </h2>
                <p className="text-sm text-gray-600 leading-relaxed">
                  {t.description}
                </p>
              </div>
            </article>
          </Link>
        ))}
      </section>
    </main>
  );
}

function Plaza() {
  const { topicId } = useParams();
  const nav = useNavigate();
  const topic = topics.find((t) => t.id === topicId);
  const [subtopics, setSubtopics] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  // Fetch subtopics for this topic
  useEffect(() => {
    const fetchSubtopics = async () => {
      if (!topicId || !topic?.category) return;
      
      try {
        setIsLoading(true);
        
        const response = await fetch(`${API_BASE_URL}/api/subtopics/${topic.category}`);
        
        if (!response.ok) {
          throw new Error(`Backend API error: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success && data.subtopics) {
          setSubtopics(data.subtopics);
        } else {
          throw new Error(`Backend error: ${data.message || 'Invalid response'}`);
        }
        
      } catch (error) {
        console.error('Error fetching subtopics:', error);
        setSubtopics([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchSubtopics();
  }, [topicId, topic]);

  if (!topic) {
    return (
      <main className="max-w-3xl mx-auto px-4 py-10">
        <button onClick={() => nav(-1)} className="underline">← Back</button>
        <p className="mt-6">Topic not found.</p>
      </main>
    );
  }

  if (isLoading) {
    return (
      <main className="max-w-3xl mx-auto px-4 pt-8 pb-24">
        <header className="mb-4">
          <button onClick={() => nav(-1)} className="underline">← Back</button>
          <h1 className="text-4xl md:text-5xl font-black leading-tight mt-3">
            {topic.title}
          </h1>
        </header>
        <div className="hr my-6"></div>
        <div className="text-center py-10">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[color:var(--ink)] mx-auto"></div>
          <p className="mt-4 text-[color:var(--ink-light)]">Loading subtopics...</p>
        </div>
      </main>
    );
  }

  return (
    <main className="max-w-3xl mx-auto px-4 pt-8 pb-24">
      <header className="mb-4">
        <button onClick={() => nav(-1)} className="underline">← Back</button>
        <h1 className="text-4xl md:text-5xl font-black leading-tight mt-3">
          {topic.title}
        </h1>
        <p className="text-lg text-[color:var(--ink-light)] mt-2">
          {topic.description}
        </p>
      </header>

      <div className="hr my-6"></div>

      <section aria-labelledby="subtopics" className="mb-10">
        <h2 id="subtopics" className="text-xl font-black mb-4">This Week's Stories</h2>
        <div className="space-y-4">
          {subtopics.length > 0 ? subtopics.map((subtopic) => (
            <Link
              key={subtopic.id}
              to={`/plaza/${topicId}/${subtopic.id}`}
              className="block p-4 border border-[color:var(--rule)] rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div className="flex justify-between items-start mb-2">
                <h3 className="font-bold text-lg">{subtopic.title}</h3>
                <span className="text-sm text-[color:var(--ink-light)] bg-gray-100 px-2 py-1 rounded">
                  {subtopic.article_count} articles
                </span>
              </div>
              <p className="text-[color:var(--ink-light)] text-sm mb-2">
                {subtopic.description}
              </p>
              {subtopic.latest_article && (
                <div className="text-xs text-[color:var(--ink-light)]">
                  Latest: {subtopic.latest_article.title?.substring(0, 100)}...
                </div>
              )}
            </Link>
          )) : (
            <div className="text-center py-8 text-[color:var(--ink-light)]">
              <p>No subtopics found for this week.</p>
              <p className="text-sm mt-2">Check back later for new stories.</p>
            </div>
          )}
        </div>
      </section>
    </main>
  );
}

function SubPlaza() {
  const { topicId, subtopicId } = useParams();
  const nav = useNavigate();
  const topic = topics.find((t) => t.id === topicId);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [articles, setArticles] = useState([]);
  const [subtopic, setSubtopic] = useState(null);
  const [conversationStyle, setConversationStyle] = useState("casual");
  const [isPlaying, setIsPlaying] = useState(false);
  const messagesEndRef = useRef(null);

  // Debug environment variables
  console.log('=== ENVIRONMENT DEBUG ===');
  console.log('NODE_ENV:', process.env.NODE_ENV);
  console.log('All env vars:', Object.keys(process.env).filter(key => key.startsWith('REACT_APP')));
  console.log('REACT_APP_NEWS_API_KEY exists:', !!process.env.REACT_APP_NEWS_API_KEY);
  console.log('REACT_APP_NEWS_API_KEY value:', process.env.REACT_APP_NEWS_API_KEY);
  console.log('========================');

  // Simple text-to-speech functionality
  const speakConversation = async () => {
    console.log('Play button clicked!', { isPlaying, messagesLength: messages?.length });
    
    if (isPlaying) {
      // Stop current speech
      console.log('Stopping speech...');
      setIsPlaying(false);
      if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
      }
      return;
    }

    if (!messages || messages.length === 0) {
      console.log('No messages to speak');
      return;
    }

    if (!window.speechSynthesis) {
      console.error('Web Speech API not supported');
      alert('Text-to-speech is not supported in this browser');
      return;
    }

    console.log('Starting speech...');
    setIsPlaying(true);
    let currentIndex = 0;

    const speakNextMessage = () => {
      console.log(`Speaking message ${currentIndex + 1}/${messages.length}`);
      if (currentIndex >= messages.length) {
        console.log('Finished speaking all messages');
        setIsPlaying(false);
        return;
      }

      const message = messages[currentIndex];
      const textToSpeak = `${message.speaker} says: ${message.text}`;
      console.log('Speaking:', textToSpeak);

      const utterance = new SpeechSynthesisUtterance(textToSpeak);
      utterance.rate = 0.9;
      utterance.pitch = 1;
      utterance.volume = 0.8;
      
      utterance.onend = () => {
        console.log('Message ended, moving to next');
        currentIndex++;
        setTimeout(speakNextMessage, 500);
      };
      
      utterance.onerror = (error) => {
        console.error('Speech synthesis error:', error);
        setIsPlaying(false);
      };
      
      window.speechSynthesis.speak(utterance);
    };

    speakNextMessage();
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Cleanup speech synthesis when component unmounts
  useEffect(() => {
    return () => {
      // Stop any ongoing speech
      setIsPlaying(false);
      if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);


  // Simple bias analysis based on content
  const analyzeContentBias = (text) => {
    if (!text) return 0;

    const textLower = text.toLowerCase();
    let biasScore = 0;

    // Simple bias indicators
    const biasWords = [
      'outrageous', 'shocking', 'devastating', 'terrible', 'awful', 'horrible',
      'clearly', 'obviously', 'undoubtedly', 'certainly', 'definitely',
      'i believe', 'i think', 'in my opinion', 'personally', 'i feel',
      'finally', 'not surprisingly', 'of course', 'unfortunately', 'sadly',
      'very', 'extremely', 'incredibly', 'absolutely', 'completely'
    ];

    // Count bias words
    biasWords.forEach(word => {
      if (textLower.includes(word)) {
        biasScore += 0.1;
      }
    });

    // Check for punctuation
    const questionMarks = (text.match(/\?/g) || []).length;
    const exclamationMarks = (text.match(/!/g) || []).length;
    biasScore += (questionMarks + exclamationMarks) * 0.05;

    return Math.min(1, biasScore);
  };

  // Get bias shading based on content analysis
  const getBiasShading = (text) => {
    const biasIntensity = analyzeContentBias(text);
    
    // Return opacity based on bias (0.1 = very light, 0.9 = very dark)
    const opacity = 0.1 + (biasIntensity * 0.8);
    
    return {
      backgroundColor: `rgba(107, 114, 128, ${opacity})`, // Grey with varying opacity
      borderColor: `rgba(107, 114, 128, ${opacity + 0.2})`
    };
  };

  // Fetch subtopic data
  useEffect(() => {
    const fetchSubtopicData = async () => {
      if (!topicId || !subtopicId || !topic?.category) return;
      
      try {
        setIsLoading(true);
        
        const response = await fetch(`${API_BASE_URL}/api/subtopic/${topic.category}/${subtopicId}?style=${conversationStyle}`);
        
        if (!response.ok) {
          throw new Error(`Backend API error: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
          setSubtopic(data.subtopic);
          setArticles(data.articles || []);
          setMessages(data.conversation || []);
        } else {
          throw new Error(`Backend error: ${data.message || 'Invalid response'}`);
        }
        
      } catch (error) {
        console.error('Error fetching subtopic data:', error);
        setArticles([]);
        setMessages([{
          id: 1,
          speaker: "System",
          side: "left",
          text: `Error loading subtopic: ${error.message}`,
          timestamp: new Date().toISOString()
        }]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchSubtopicData();
  }, [topicId, subtopicId, topic, conversationStyle]);


  if (!topic) {
    return (
      <main className="max-w-3xl mx-auto px-4 py-10">
        <button onClick={() => nav(-1)} className="underline">← Back</button>
        <p className="mt-6">Topic not found.</p>
      </main>
    );
  }

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isTyping) return;

    const userMessage = {
      id: Date.now(),
      speaker: "You",
      side: "right",
      text: inputValue.trim(),
      isUser: true,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue("");
    setIsTyping(true);

    try {
      // Send message to backend for AI response
      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputValue.trim(),
          topic: topic?.title || '',
          subtopic: subtopic?.title || '',
          articles: articles,
          history: messages.slice(-5), // Last 5 messages for context
          style: conversationStyle
        })
      });

      if (!response.ok) {
        throw new Error(`Backend API error: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.success && data.response) {
        setMessages(prev => [...prev, data.response]);
      } else {
        throw new Error(data.message || 'Invalid response');
      }
      
    } catch (error) {
      console.error('Error sending message:', error);
      // Fallback response
      const fallbackResponse = {
        id: Date.now() + 1,
        speaker: "System",
        side: "left",
        text: "I'm having trouble processing your message right now. Please try again.",
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, fallbackResponse]);
    } finally {
      setIsTyping(false);
    }
  };



  if (!topic) {
    return (
      <main className="max-w-3xl mx-auto px-4 py-10">
        <button onClick={() => nav(-1)} className="underline">← Back</button>
        <p className="mt-6">Topic not found.</p>
      </main>
    );
  }

  if (isLoading) {
    return (
      <main className="max-w-3xl mx-auto px-4 pt-8 pb-24">
        <header className="mb-4">
          <button onClick={() => nav(-1)} className="underline">← Back</button>
          <h1 className="text-4xl md:text-5xl font-black leading-tight mt-3">
            {subtopic?.title || 'Loading...'}
          </h1>
        </header>
        <div className="hr my-6"></div>
        <div className="text-center py-10">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[color:var(--ink)] mx-auto"></div>
          <p className="mt-4 text-[color:var(--ink-light)]">Loading conversation and articles...</p>
        </div>
      </main>
    );
  }

  return (
    <main className="max-w-3xl mx-auto px-4 pt-8 pb-24">
      <header className="mb-4">
        <button onClick={() => nav(-1)} className="underline">← Back</button>
        <h1 className="text-4xl md:text-5xl font-black leading-tight mt-3">
          {subtopic?.title || 'Subtopic'}
        </h1>
        <p className="text-lg text-[color:var(--ink-light)] mt-2">
          {subtopic?.description}
        </p>
      </header>

      <div className="hr my-6"></div>

      {/* Articles summary */}
      <section aria-labelledby="articles" className="mb-10">
        <h2 id="articles" className="text-xl font-black mb-3">Latest News Summary</h2>
        <ul className="space-y-2 text-[color:var(--ink-light)]">
          {articles.length > 0 ? articles.slice(0, 4).map((article, i) => (
            <li key={i} className="pl-4 relative">
              <span className="absolute left-0 top-0">•</span>
              <a href={article.url} target="_blank" rel="noopener noreferrer" className="hover:underline">
                {article.title}: {article.summary || article.description?.substring(0, 150)}...
              </a>
            </li>
          )) : (
            <li className="pl-4 relative">
              <span className="absolute left-0 top-0">•</span>Loading recent news about this topic...
            </li>
          )}
        </ul>
      </section>

      <div className="hr my-6"></div>

      {/* Chat area */}
      <section aria-labelledby="chat">
        <div className="flex justify-between items-center mb-4">
          <h2 id="chat" className="text-xl font-black">Conversation</h2>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-3 text-xs">
              <div className="flex items-center gap-1">
                <div className="w-4 h-2 rounded" style={{backgroundColor: 'rgba(107, 114, 128, 0.1)'}}></div>
                <span className="text-[color:var(--ink-light)]">Neutral</span>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-4 h-2 rounded" style={{backgroundColor: 'rgba(107, 114, 128, 0.3)'}}></div>
                <span className="text-[color:var(--ink-light)]">Light</span>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-4 h-2 rounded" style={{backgroundColor: 'rgba(107, 114, 128, 0.5)'}}></div>
                <span className="text-[color:var(--ink-light)]">Medium</span>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-4 h-2 rounded" style={{backgroundColor: 'rgba(107, 114, 128, 0.7)'}}></div>
                <span className="text-[color:var(--ink-light)]">High</span>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-4 h-2 rounded" style={{backgroundColor: 'rgba(107, 114, 128, 0.9)'}}></div>
                <span className="text-[color:var(--ink-light)]">Very High</span>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <label htmlFor="style-select" className="text-sm text-[color:var(--ink-light)]">
                Style:
              </label>
              <select
                id="style-select"
                value={conversationStyle}
                onChange={(e) => setConversationStyle(e.target.value)}
                className="px-3 py-1 border border-[color:var(--rule)] rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="casual">Casual</option>
                <option value="genz">Gen Z</option>
              </select>
            </div>
            <button
              onClick={speakConversation}
              className={`flex items-center gap-2 px-3 py-1 rounded text-sm transition-colors ${
                isPlaying 
                  ? 'bg-red-100 text-red-700 hover:bg-red-200' 
                  : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
              }`}
              title={isPlaying ? "Stop reading conversation" : "Read conversation aloud"}
            >
              {isPlaying ? (
                <>
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1zm4 0a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  Stop
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
                  </svg>
                  Play
                </>
              )}
            </button>
          </div>
        </div>
        <div className="space-y-4 mb-6 max-h-96 overflow-y-auto">
          {messages.map((m, i) => {
            // Get bias shading for the message
            const biasShading = getBiasShading(m.text);
            
            return (
              <div key={m.id || i} className={`flex ${m.side === "left" ? "justify-start" : "justify-end"}`}>
                <div 
                  className="max-w-[85%] rounded-2xl px-4 py-3 border text-sm leading-6"
                  style={{
                    backgroundColor: m.side === "left" ? biasShading.backgroundColor : "#f4f3f1",
                    borderColor: m.side === "left" ? biasShading.borderColor : "#e6e4e0"
                  }}
                >
                  <div 
                    className="font-bold mb-1 cursor-pointer transition-colors duration-200 hover:text-blue-600"
                    title={m.news_source ? `News Source: ${m.news_source}${(m.news_source_url || m.source_url) ? ' (Click to read article)' : ''}` : ''}
                    onMouseEnter={(e) => {
                      if (m.news_source) {
                        e.target.textContent = m.news_source;
                        e.target.style.textDecoration = 'underline';
                        e.target.dataset.showingSource = 'true';
                      }
                    }}
                    onMouseLeave={(e) => {
                      e.target.textContent = m.speaker;
                      e.target.style.textDecoration = 'none';
                      e.target.dataset.showingSource = 'false';
                    }}
                    onClick={(e) => {
                      const url = m.news_source_url || m.source_url;
                      const isShowingSource = e.target.dataset.showingSource === 'true';
                      
                      if (url && isShowingSource) {
                        window.open(url, '_blank', 'noopener,noreferrer');
                      }
                    }}
                  >
                    {m.speaker}
                  </div>
                  <p className="text-[color:var(--ink-light)]">{m.text}</p>
                </div>
              </div>
            );
          })}
          {isTyping && (
            <div className="flex justify-start">
              <div className="max-w-[85%] rounded-2xl px-4 py-3 border text-sm leading-6 bg-white border-[color:var(--rule)]">
                <div className="font-bold mb-1">Someone is typing...</div>
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Chat input */}
        <form onSubmit={handleSendMessage} className="flex gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Ask a question or share your thoughts..."
            className="flex-1 px-4 py-3 border border-[color:var(--rule)] rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={isTyping}
          />
          <button
            type="submit"
            disabled={!inputValue.trim() || isTyping}
            className="px-6 py-3 bg-[color:var(--ink)] text-white rounded-lg hover:bg-[color:var(--ink-light)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Send
          </button>
        </form>
      </section>

      {/* bottom spacer so chat isn't cramped on mobile */}
      <div className="h-20" />
    </main>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/plaza/:topicId" element={<Plaza />} />
      <Route path="/plaza/:topicId/:subtopicId" element={<SubPlaza />} />
    </Routes>
  );
}
