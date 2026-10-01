"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { demoEvents } from "@/lib/demo-data";

export default function SearchPage() {
  const [query, setQuery] = useState("");

  const results = useMemo(() => {
    const q = query.toLowerCase().trim();

    if (!q) return demoEvents;

    return demoEvents.filter((event) =>
      [
        event.home.name,
        event.away.name,
        event.league.name,
        event.sport,
      ]
        .join(" ")
        .toLowerCase()
        .includes(q)
    );
  }, [query]);

  return (
    <main className="mx-auto max-w-4xl px-4 py-8">
      <Link href="/" className="text-sm text-emerald-400">
        ← Home
      </Link>

      <h1 className="mt-6 text-3xl font-black">
        Search
      </h1>

      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search teams, leagues or sports..."
        className="mt-6 w-full rounded-2xl border border-zinc-800 bg-zinc-950 px-4 py-4 outline-none focus:border-emerald-400"
      />

      <div className="mt-6 space-y-3">
        {results.map((event) => (
          <Link
            key={event.id}
            href={`/events/${event.id}`}
            className="block rounded-2xl border border-zinc-800 p-4 hover:bg-zinc-900"
          >
            <div className="text-xs text-zinc-500">
              {event.league.name}
            </div>

            <div className="mt-2 font-bold">
              {event.home.name} vs {event.away.name}
            </div>
          </Link>
        ))}
      </div>
    </main>
  );
}
