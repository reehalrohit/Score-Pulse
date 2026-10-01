"use client";

import { useEffect, useState } from "react";
import { getLiveEvents } from "@/lib/api";
import { LiveEvent } from "@/lib/types";
import LiveMatchCard from "./LiveMatchCard";

export default function ScorePulseDashboard({
  sport = "all",
}: {
  sport?: string;
}) {
  const [events, setEvents] = useState<LiveEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [lastUpdated, setLastUpdated] =
    useState<Date | null>(null);

  async function load() {
    try {
      setError("");

      const data = await getLiveEvents();

      setEvents(data);
      setLastUpdated(new Date());
    } catch (err) {
      console.error(err);
      setError("Live scores are temporarily unavailable.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();

    const timer = setInterval(load, 30000);

    return () => clearInterval(timer);
  }, []);

  const filteredEvents =
    sport === "all"
      ? events
      : events.filter(
          (event) => event.sport === sport
        );

  if (loading) {
    return (
      <div className="py-20 text-center text-zinc-400">
        <div className="mx-auto mb-4 h-8 w-8 animate-spin rounded-full border-2 border-zinc-700 border-t-emerald-400" />
        Loading live scores…
      </div>
    );
  }

  return (
    <section className="space-y-4">
      {error && (
        <div className="rounded-2xl border border-amber-500/20 bg-amber-500/5 p-4 text-sm text-amber-300">
          {error}
        </div>
      )}

      <div className="flex items-center justify-between text-xs text-zinc-500">
        <span>
          {filteredEvents.length} event
          {filteredEvents.length === 1 ? "" : "s"}
        </span>

        <span>
          {lastUpdated
            ? `Updated ${lastUpdated.toLocaleTimeString([], {
                hour: "2-digit",
                minute: "2-digit",
              })}`
            : "Waiting for update"}
        </span>
      </div>

      {filteredEvents.length === 0 ? (
        <div className="rounded-2xl border border-zinc-800 bg-zinc-950 p-8 text-center">
          <div className="text-lg font-bold">
            No live events
          </div>

          <p className="mt-2 text-sm text-zinc-500">
            There are no events available for this sport
            right now.
          </p>
        </div>
      ) : (
        filteredEvents.map((event) => (
          <LiveMatchCard
            key={event.id}
            event={event}
          />
        ))
      )}
    </section>
  );
      }
