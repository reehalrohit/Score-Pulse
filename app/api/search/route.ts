"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { LiveEvent } from "@/lib/types";

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] =
    useState<LiveEvent[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const value = query.trim();

    if (!value) {
      setResults([]);
      return;
    }

    const timer = setTimeout(async () => {
      try {
        setLoading(true);

        const response = await fetch(
          `/api/search?q=${encodeURIComponent(value)}`,
          {
            cache: "no-store",
          }
        );

        const data = await response.json();

        setResults(
          Array.isArray(data.results)
            ? data.results
            : []
        );
      } catch {
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 250);

    return () => clearTimeout(timer);
  }, [query]);

  return (
    <main className="mx-auto max-w-4xl px-4 py-8">
      <Link
        href="/"
        className="text-sm text-emerald-400"
      >
        ← Home
      </Link>

      <h1 className="mt-6 text-3xl font-black">
        Search
      </h1>

      <p className="mt-2 text-sm text-zinc-500">
        Search teams, leagues and sports.
      </p>

      <div className="relative mt-6">
        <input
          autoFocus
          value={query}
          onChange={(e) =>
            setQuery(e.target.value)
          }
          placeholder="Search teams, leagues or sports..."
          className="w-full rounded-2xl border border-zinc-800 bg-zinc-950 px-4 py-4 pr-12 outline-none transition focus:border-emerald-400"
        />

        {loading && (
          <div className="absolute right-4 top-1/2 h-5 w-5 -translate-y-1/2 animate-spin rounded-full border-2 border-zinc-700 border-t-emerald-400" />
        )}
      </div>

      {!query && (
        <div className="mt-8 rounded-2xl border border-zinc-800 bg-zinc-950 p-8 text-center">
          <div className="text-lg font-bold">
            Search Score Pulse
          </div>

          <p className="mt-2 text-sm text-zinc-500">
            Find teams, leagues and live events.
          </p>
        </div>
      )}

      {query && !loading && results.length === 0 && (
        <div className="mt-8 rounded-2xl border border-zinc-800 p-8 text-center">
          <div className="font-bold">
            No results found
          </div>

          <p className="mt-2 text-sm text-zinc-500">
            Try a team, league or sport name.
          </p>
        </div>
      )}

      <div className="mt-6 space-y-3">
        {results.map((event) => (
          <Link
            key={event.id}
            href={`/events/${encodeURIComponent(event.id)}`}
            className="block rounded-2xl border border-zinc-800 bg-zinc-950 p-4 transition hover:border-zinc-600 hover:bg-zinc-900"
          >
            <div className="flex items-center justify-between gap-4">
              <div>
                <div className="text-xs text-zinc-500">
                  {event.league.name}
                </div>

                <div className="mt-2 font-bold">
                  {event.home.name}{" "}
                  <span className="text-zinc-600">
                    vs
                  </span>{" "}
                  {event.away.name}
                </div>
              </div>

              <div className="text-xs uppercase text-zinc-600">
                {event.sport}
              </div>
            </div>
          </Link>
        ))}
      </div>
    </main>
  );
          }
