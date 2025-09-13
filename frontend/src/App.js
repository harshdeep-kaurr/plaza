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
          Plaza
        </h1>
        <h2 className="text-2xl font-bold text-[color:var(--ink-light)] mt-2">
          Explore Different Perspectives
        </h2>
        <div className="hr my-6"></div>
        <p className="text-lg text-[color:var(--ink-light)] max-w-3xl">
          A front page of conversations. Choose a topic to enter its plaza.
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
            <article className="bg-white shadow-sm ring-1 ring-[color:var(--rule)] h-80 flex flex-col">
              <div className="flex-1 overflow-hidden">
                <img
                  src={t.image}
                  alt={t.title}
                  className="w-full h-full object-cover"
                  loading="lazy"
                />
              </div>
              <div className="p-4 h-20 flex items-center">
                <h2 className="font-black text-2xl leading-snug">
                  {t.title}
                </h2>
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
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [articles, setArticles] = useState([]);
  const [facts, setFacts] = useState([]);
  const messagesEndRef = useRef(null);

  // Debug environment variables
  console.log('=== ENVIRONMENT DEBUG ===');
  console.log('NODE_ENV:', process.env.NODE_ENV);
  console.log('All env vars:', Object.keys(process.env).filter(key => key.startsWith('REACT_APP')));
  console.log('REACT_APP_NEWS_API_KEY exists:', !!process.env.REACT_APP_NEWS_API_KEY);
  console.log('REACT_APP_NEWS_API_KEY value:', process.env.REACT_APP_NEWS_API_KEY);
  console.log('========================');

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Fetch topic data from News API
  useEffect(() => {
    const fetchTopicData = async () => {
      if (!topicId || !topic?.category) return;
      
      try {
        setIsLoading(true);
        
        // Calculate date range for past week
        const oneWeekAgo = new Date();
        oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);
        const fromDate = oneWeekAgo.toISOString().split('T')[0];
        const toDate = new Date().toISOString().split('T')[0];
        
        // Fetch news articles through backend API
        console.log('Fetching news for category:', topic.category);
        
        // Convert category to search query
        const searchQuery = getSearchQueryForCategory(topic.category);
        console.log('Search query:', searchQuery);
        
        const params = new URLSearchParams({
          q: searchQuery,
          days: 7
        });
        
        const backendResponse = await fetch(`${API_BASE_URL}/api/news?${params}`);
        
        if (!backendResponse.ok) {
          throw new Error(`Backend API error: ${backendResponse.status}`);
        }
        
        const newsData = await backendResponse.json();
        console.log('Backend news response:', newsData);
        
        if (newsData.success && newsData.articles) {
          setArticles(newsData.articles);
          
          // Check if we have articles
          if (newsData.articles.length > 0) {
            // Generate facts from articles
            const generatedFacts = generateFactsFromArticles(newsData.articles, topic.category);
            setFacts(generatedFacts);
            
            // Generate initial chat discussion
            const initialChat = generateInitialChat(newsData.articles, topic.category);
            setMessages(initialChat);
          } else {
            // No articles found, show debug info
            setFacts([`No articles found for ${topic.category}. Backend Response: ${JSON.stringify(newsData, null, 2)}`]);
            setMessages([{
              id: 1,
              speaker: "Debug Info",
              side: "left",
              text: `Backend returned ${newsData.total_articles || 0} articles for category: ${topic.category}`,
              timestamp: new Date().toISOString()
            }]);
          }
        } else {
          throw new Error(`Backend error: ${newsData.message || 'Invalid response'}`);
        }
        
      } catch (error) {
        console.error('Error fetching news data:', error);
        // Show debug info instead of fallback content
        setArticles([]);
        setFacts([`Error fetching news: ${error.message}. Check console for details.`]);
        setMessages([{
          id: 1,
          speaker: "Debug Error",
          side: "left",
          text: `Backend API Error: ${error.message}. Make sure your backend is running and has the News API key in backend/.env`,
          timestamp: new Date().toISOString()
        }]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchTopicData();
  }, [topicId, topic]);

  // Get search query for News API based on category
  const getSearchQueryForCategory = (category) => {
    const searchQueries = {
      'business': 'business economy finance market stocks',
      'entertainment': 'entertainment movies music tv celebrities',
      'health': 'health medical research healthcare medicine',
      'science': 'science research technology innovation discovery',
      'sports': 'sports football basketball soccer tennis',
      'technology': 'technology AI artificial intelligence software tech'
    };
    
    return searchQueries[category] || category;
  };

  // Generate fallback facts when API fails
  const generateFallbackFacts = (category) => {
    const fallbackFacts = {
      'business': [
        "Market trends continue to evolve with changing economic conditions.",
        "Corporate earnings reports show mixed results across different sectors.",
        "Investor sentiment remains cautious amid global economic uncertainty."
      ],
      'entertainment': [
        "New releases continue to shape the entertainment landscape.",
        "Streaming platforms are investing heavily in original content.",
        "Award season brings attention to outstanding performances and productions."
      ],
      'health': [
        "Medical research continues to advance treatment options.",
        "Public health initiatives focus on preventive care and wellness.",
        "Healthcare systems adapt to changing patient needs and technology."
      ],
      'science': [
        "Scientific discoveries continue to expand our understanding of the world.",
        "Research institutions collaborate on breakthrough innovations.",
        "Technology and science intersect to solve complex global challenges."
      ],
      'sports': [
        "Athletes continue to push the boundaries of human performance.",
        "Major tournaments and championships draw global attention.",
        "Sports technology and training methods continue to evolve."
      ],
      'technology': [
        "Artificial intelligence and machine learning drive innovation across industries.",
        "Cybersecurity remains a top priority for organizations worldwide.",
        "Emerging technologies continue to transform how we work and live."
      ],
      'general': [
        "Global events continue to shape international relations and policies.",
        "Social and economic developments impact communities worldwide.",
        "Breaking news stories capture public attention and drive discussions."
      ]
    };
    
    return fallbackFacts[category] || ["Recent developments in this area are being closely monitored."];
  };

  // Generate fallback chat when API fails
  const generateFallbackChat = (category) => {
    const personas = [
      { name: "Financial Reporter", outlet: "Financial Times" },
      { name: "Tech Journalist", outlet: "TechCrunch" },
      { name: "General Reporter", outlet: "Associated Press" }
    ];
    
    const categoryMessages = {
      'business': [
        "Market analysts are closely watching economic indicators and corporate earnings.",
        "Investment strategies continue to adapt to changing market conditions.",
        "Business leaders are navigating complex regulatory and economic landscapes."
      ],
      'entertainment': [
        "The entertainment industry continues to evolve with new platforms and content.",
        "Award shows and festivals highlight outstanding creative achievements.",
        "Streaming services are reshaping how audiences consume entertainment."
      ],
      'health': [
        "Medical professionals continue to advance treatment options and patient care.",
        "Public health initiatives focus on prevention and community wellness.",
        "Healthcare technology is transforming how medical services are delivered."
      ],
      'science': [
        "Scientific research continues to push the boundaries of human knowledge.",
        "Collaborative efforts between institutions drive breakthrough discoveries.",
        "Technology and science work together to address global challenges."
      ],
      'sports': [
        "Athletes continue to achieve remarkable feats and break records.",
        "Sports organizations adapt to changing fan expectations and technology.",
        "Training methods and sports science continue to evolve."
      ],
      'technology': [
        "Tech companies continue to innovate and shape the digital landscape.",
        "Artificial intelligence and automation are transforming industries.",
        "Cybersecurity and data privacy remain critical concerns."
      ],
      'general': [
        "Global events continue to shape international relations and policies.",
        "Social and economic developments impact communities worldwide.",
        "Breaking news stories capture public attention and drive discussions."
      ]
    };
    
    const messages = categoryMessages[category] || ["Recent developments in this area are being closely monitored."];
    
    return messages.map((text, index) => ({
      id: index + 1,
      speaker: `${personas[index % personas.length].name} (${personas[index % personas.length].outlet})`,
      side: index % 2 === 0 ? "left" : "right",
      text: text,
      timestamp: new Date().toISOString()
    }));
  };

  // Generate facts from news articles
  const generateFactsFromArticles = (articles, category) => {
    if (!articles || articles.length === 0) {
      return [`No recent news found for ${category} category.`];
    }
    
    const facts = [];
    const topArticles = articles.slice(0, 5); // Use top 5 articles
    
    topArticles.forEach((article, index) => {
      if (article.title && article.description) {
        // Create a fact from the article title and description
        const fact = `${article.title}: ${article.description.substring(0, 150)}...`;
        facts.push(fact);
      }
    });
    
    return facts.length > 0 ? facts : [`Recent developments in ${category} are being closely monitored.`];
  };

  // Generate initial chat discussion from news articles
  const generateInitialChat = (articles, category) => {
    if (!articles || articles.length === 0) {
      return [{
        id: 1,
        speaker: "News Analyst",
        side: "left",
        text: `No recent news found for ${category} category. Check back later for updates.`,
        timestamp: new Date().toISOString()
      }];
    }
    
    const chat = [];
    const topArticles = articles.slice(0, 3); // Use top 3 articles for initial discussion
    
    const personas = [
      { name: "Financial Reporter", outlet: "Financial Times" },
      { name: "Tech Journalist", outlet: "TechCrunch" },
      { name: "General Reporter", outlet: "Associated Press" }
    ];
    
    topArticles.forEach((article, index) => {
      const persona = personas[index % personas.length];
      const message = {
        id: index + 1,
        speaker: `${persona.name} (${persona.outlet})`,
        side: index % 2 === 0 ? "left" : "right",
        text: `${article.title}: ${article.description?.substring(0, 200)}...`,
        timestamp: new Date().toISOString()
      };
      chat.push(message);
    });
    
    return chat;
  };

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
      // Generate AI responses based on news articles and user input
      const aiResponses = generateAIResponses(inputValue.trim(), articles, topic?.category);
      
      // Add responses with staggered timing
      aiResponses.forEach((response, index) => {
        setTimeout(() => {
          setMessages(prev => [...prev, response]);
        }, (index + 1) * 1000);
      });
      
    } catch (error) {
      console.error('Error generating AI response:', error);
      // Fallback response
      const fallbackResponse = {
        id: Date.now() + 1,
        speaker: "News Analyst",
        side: "left",
        text: "I'm having trouble processing your message right now. Please try again.",
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, fallbackResponse]);
    } finally {
      setIsTyping(false);
    }
  };

  // Generate AI responses based on news articles
  const generateAIResponses = (userInput, articles, category) => {
    const responses = [];
    const numResponses = Math.random() > 0.5 ? 2 : 1;
    
    const personas = [
      { name: "Financial Reporter", outlet: "Financial Times" },
      { name: "Tech Journalist", outlet: "TechCrunch" },
      { name: "General Reporter", outlet: "Associated Press" },
      { name: "Science Writer", outlet: "Scientific American" },
      { name: "Business Analyst", outlet: "Wall Street Journal" }
    ];
    
    for (let i = 0; i < numResponses; i++) {
      const persona = personas[Math.floor(Math.random() * personas.length)];
      const response = generatePersonaResponse(userInput, persona, articles, category);
      responses.push(response);
    }
    
    return responses;
  };

  // Generate response for a specific persona
  const generatePersonaResponse = (userInput, persona, articles, category) => {
    const baseResponses = {
      "Financial Reporter": [
        "From a financial perspective, this development could have significant market implications.",
        "The economic data suggests interesting trends that investors should monitor closely.",
        "This could impact various sectors differently depending on implementation and timing."
      ],
      "Tech Journalist": [
        "The technological implications of this are quite significant and evolving rapidly.",
        "From an innovation standpoint, this represents both opportunities and challenges.",
        "The tech industry is closely watching how this develops given the potential impact."
      ],
      "General Reporter": [
        "This is a developing story that we're continuing to monitor closely.",
        "The facts are still emerging and we're working to verify all information.",
        "This situation requires careful fact-checking and multiple source verification."
      ],
      "Science Writer": [
        "The scientific community has been discussing this topic extensively with fascinating findings.",
        "Recent studies have provided new insights that challenge some previous assumptions.",
        "This is an area where interdisciplinary research is particularly valuable."
      ],
      "Business Analyst": [
        "From a business standpoint, this could have significant implications for market dynamics.",
        "The economic data shows interesting trends that investors should be watching closely.",
        "This development could impact various sectors differently depending on implementation."
      ]
    };

    const personaResponses = baseResponses[persona.name] || ["That's an interesting perspective on this topic."];
    const randomResponse = personaResponses[Math.floor(Math.random() * personaResponses.length)];
    
    // If we have relevant articles, reference them
    let responseText = randomResponse;
    if (articles && articles.length > 0) {
      const relevantArticle = articles[Math.floor(Math.random() * Math.min(articles.length, 3))];
      if (relevantArticle) {
        responseText += ` For example, recent reports show that ${relevantArticle.title?.substring(0, 100)}...`;
      }
    }
    
    return {
      id: Date.now() + Math.random(),
      speaker: `${persona.name} (${persona.outlet})`,
      side: "left",
      text: responseText,
      isUser: false,
      timestamp: new Date().toISOString()
    };
  };


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
          <p className="mt-4 text-[color:var(--ink-light)]">Loading latest news and perspectives...</p>
        </div>
      </main>
    );
  }

  return (
    <main className="max-w-3xl mx-auto px-4 pt-8 pb-24">
      {/* Minimalist top */}
      <header className="mb-4">
        <button onClick={() => nav(-1)} className="underline">← Back</button>
        <h1 className="text-4xl md:text-5xl font-black leading-tight mt-3">
          {topic.title}
        </h1>
      </header>

      <div className="hr my-6"></div>

      {/* Known facts */}
      <section aria-labelledby="facts" className="mb-10">
        <h2 id="facts" className="text-xl font-black mb-3">Latest News Summary</h2>
        <ul className="space-y-2 text-[color:var(--ink-light)]">
          {facts.length > 0 ? facts.map((f, i) => (
            <li key={i} className="pl-4 relative">
              <span className="absolute left-0 top-0">•</span>{f}
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
        <h2 id="chat" className="text-xl font-black mb-4">Conversation</h2>
        <div className="space-y-4 mb-6 max-h-96 overflow-y-auto">
          {messages.map((m, i) => (
            <div key={m.id || i} className={`flex ${m.side === "left" ? "justify-start" : "justify-end"}`}>
              <div className={`max-w-[85%] rounded-2xl px-4 py-3 border text-sm leading-6
                              ${m.side === "left" ? "bg-white" : "bg-[#f4f3f1]"} 
                              border-[color:var(--rule)]`}>
                <div className="font-bold mb-1">{m.speaker}</div>
                <p className="text-[color:var(--ink-light)]">{m.text}</p>
                {m.source && (
                  <div className="mt-2 text-xs text-[color:var(--ink-light)]">
                    Source: <a className="underline" href={m.source} target="_blank" rel="noreferrer">link</a>
                  </div>
                )}
              </div>
            </div>
          ))}
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
    </Routes>
  );
}
