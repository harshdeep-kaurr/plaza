import { useEffect, useState } from "react";

function SubtopicGrid({ category, onOpenPlaza }) {
  const [loading, setLoading] = useState(true);
  const [subtopics, setSubtopics] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    let abort = false;
    setLoading(true);
    fetch(`/api/category/${encodeURIComponent(category)}/topics?days=7&k=6`)
      .then(r => r.json())
      .then(data => {
        if (abort) return;
        if (data.success) setSubtopics(data.subtopics);
        else setError(data.message || "Failed to load subtopics");
      })
      .catch(() => !abort && setError("Network error"))
      .finally(() => !abort && setLoading(false));
    return () => { abort = true; };
  }, [category]);

  if (loading) return <div className="p-4">Loading {category}…</div>;
  if (error) return <div className="p-4 text-red-600">{error}</div>;

  return (
    <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 p-4">
      {subtopics.map(t => (
        <button
          key={t.id}
          className="text-left rounded-2xl shadow p-4 hover:shadow-lg transition"
          onClick={() =>
            onOpenPlaza({
              displayName: t.label,
              // pass category + refined query to the plaza page
              fetchUrl: `/api/topic/${encodeURIComponent(category)}?q=${encodeURIComponent(t.query_hint)}`
            })
          }
        >
          <div className="font-semibold text-lg mb-1">{t.label}</div>
          <div className="text-xs text-gray-500 mb-2">
            {t.article_count} related articles • {t.top_terms.slice(0,3).join(" · ")}
          </div>
          <ul className="list-disc pl-5 text-sm space-y-1">
            {t.sample_headlines.slice(0,4).map((h, i) => (
              <li key={i}>
                <span className="font-medium">{h.source}</span>:{" "}
                <span className="line-clamp-1">{h.title}</span>
              </li>
            ))}
          </ul>
        </button>
      ))}
    </div>
  );
}

export default SubtopicGrid;
