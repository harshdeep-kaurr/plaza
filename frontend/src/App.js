import React, { useState, useRef, useEffect } from "react";
import { Routes, Route, Link, useParams, useNavigate } from "react-router-dom";
import topics from "./data/topics";

function Home() {
  return (
    <main className="max-w-6xl mx-auto px-4 py-10">
      {/* Header */}
      <header className="mb-8">
        <h1 className="text-5xl leading-tight tracking-tight font-black">
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
  const [messages, setMessages] = useState(topic?.chat || []);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

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

    // Simulate AI responses from different personas
    setTimeout(() => {
      const responses = generateResponses(inputValue, topic);
      setMessages(prev => [...prev, ...responses]);
      setIsTyping(false);
    }, 1500);
  };

  const generateResponses = (userInput, topic) => {
    const responses = [];
    const personas = topic.chat.map(msg => msg.speaker);
    
    // Generate 1-2 responses from different personas
    const numResponses = Math.random() > 0.5 ? 2 : 1;
    const selectedPersonas = personas.sort(() => 0.5 - Math.random()).slice(0, numResponses);
    
    selectedPersonas.forEach((persona, index) => {
      setTimeout(() => {
        const response = generatePersonaResponse(userInput, persona, topic);
        setMessages(prev => [...prev, response]);
      }, (index + 1) * 1000);
    });

    return [];
  };

  const generatePersonaResponse = (userInput, persona, topic) => {
    const responses = {
      "Dr. Sarah Chen (Nature)": [
        "Based on the latest research, that's a complex question with multiple factors at play.",
        "The scientific evidence suggests we need to consider both short-term and long-term implications.",
        "From a research perspective, this highlights the importance of peer-reviewed studies and data validation."
      ],
      "Mike Rodriguez (WSJ)": [
        "From a business standpoint, this could have significant implications for market dynamics.",
        "The economic data shows interesting trends that investors should be watching closely.",
        "This development could impact various sectors differently, depending on implementation."
      ],
      "Dr. Elena Patel (Scientific American)": [
        "The scientific community has been discussing this topic extensively, with some fascinating findings.",
        "Recent studies have provided new insights that challenge some previous assumptions.",
        "This is an area where interdisciplinary research is particularly valuable."
      ],
      "Leo (MIT Tech Review)": [
        "The technological implications of this are quite significant and evolving rapidly.",
        "From an innovation perspective, this represents both opportunities and challenges.",
        "The tech industry is closely watching how this develops, given the potential impact on various sectors."
      ],
      "Rin (Financial Times)": [
        "The financial markets are responding to this development with cautious optimism.",
        "Investors are weighing the potential risks and rewards of this situation carefully.",
        "This could have broader economic implications that we're only beginning to understand."
      ],
      "Zoe (Nature)": [
        "The research community is actively investigating this phenomenon with rigorous methodologies.",
        "Peer review processes are ensuring that findings are thoroughly validated before publication.",
        "This represents an important area of scientific inquiry with significant potential impact."
      ],
      "Kai (AP)": [
        "This is a developing story that we're continuing to monitor closely.",
        "The facts are still emerging, and we're working to verify all information before reporting.",
        "This situation requires careful fact-checking and multiple source verification."
      ],
      "Jules (FiveThirtyEight)": [
        "The data suggests some interesting patterns that are worth analyzing further.",
        "Statistical models are showing some surprising correlations that need deeper investigation.",
        "This is a complex issue that requires careful data analysis and interpretation."
      ]
    };

    const personaResponses = responses[persona] || ["That's an interesting perspective on this topic."];
    const randomResponse = personaResponses[Math.floor(Math.random() * personaResponses.length)];
    
    return {
      id: Date.now() + Math.random(),
      speaker: persona,
      side: "left",
      text: randomResponse,
      isUser: false,
      timestamp: new Date().toISOString()
    };
  };

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
        <h2 id="facts" className="text-xl font-black mb-3">Known facts</h2>
        <ul className="space-y-2 text-[color:var(--ink-light)]">
          {topic.facts.map((f, i) => (
            <li key={i} className="pl-4 relative">
              <span className="absolute left-0 top-0">•</span>{f}
            </li>
          ))}
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
