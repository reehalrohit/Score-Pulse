"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { LiveEvent } from "@/lib/types";

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<LiveEvent[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const q = query.trim();

    if (!q) {
      setResults([]);
      return;
    }

    const timer = setTimeout(async () => {
      setLoading(true);

      try {
        const response = await fetch(
          `/api/search?q=${encodeURIComponent(q)}`,
          { cache: "no-store" }
        );

        const data = await response.json();
        setResults(Array.isArray(data.results) ? data.results : []);
      } catch {
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [query]);

  return (
    <main className="mx-auto min-h-screen max-w-4xl px-4 py-8">
      <Link href="/" className="text-sm text-emerald-400">
        ← Home
      </Link>

      <h1 className="mt-6 text-3xl font-black">
        Search
      </h1>

      <p className="mt-2 text-sm text-zinc-500">
        Search teams, leagues and sports from the live data feed.
      </p>

      <input
        autoFocus
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search teams, leagues or sports..."
        className="mt-6 w-full rounded-2xl border border-zinc-800 bg-zinc-950 px-4 py-4 outline-none focus:border-emerald-400"
      />

      {loading && (
        <p className="mt-4 text-sm text-zinc-500">
          Searching…
        </p>
      )}

      <div className="mt-6 space-y-3">
        {results.map((event) => (
          <Link
            key={event.id}
            href={`/events/${encodeURIComponent(event.id)}`}
            className="block rounded-2xl border border-zinc-800 bg-zinc-950 p-4 transition hover:border-zinc-600 hover:bg-zinc-900"
          >
            <p className="text-xs text-zinc-500">
              {event.league.name}
            </p>

            <p className="mt-2 font-bold">
              {event.home.name}{" "}
              <span className="text-zinc-600">vs</span>{" "}
              {event.away.name}
            </p>

            <p className="mt-1 text-xs uppercase text-zinc-600">
              {event.sport}
            </p>
          </Link>
        ))}
      </div>

      {!loading && query.trim() && results.length === 0 && (
        <div className="mt-8 rounded-2xl border border-zinc-800 bg-zinc-950 p-8 text-center">
          <p className="font-semibold">No matching events</p>
          <p className="mt-2 text-sm text-zinc-500">
            Try a team, league or sport name.
          </p>
        </div>
      )}
    </main>
  );
}
