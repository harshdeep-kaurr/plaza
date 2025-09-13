import React from "react";
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

  if (!topic) {
    return (
      <main className="max-w-3xl mx-auto px-4 py-10">
        <button onClick={() => nav(-1)} className="underline">← Back</button>
        <p className="mt-6">Topic not found.</p>
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
        <h2 id="chat" className="sr-only">Conversation</h2>
        <div className="space-y-4">
          {topic.chat.map((m, i) => (
            <div key={i} className={`flex ${m.side === "left" ? "justify-start" : "justify-end"}`}>
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
        </div>
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
