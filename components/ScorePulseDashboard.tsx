"use client";

import { useEffect, useState } from "react";
import { getLiveEvents } from "@/lib/api";
import { LiveEvent } from "@/lib/types";
import LiveMatchCard from "./LiveMatchCard";

export default function ScorePulseDashboard() {
  const [events, setEvents] = useState<LiveEvent[]>([]);
  const [loading, setLoading] = useState(true);

  async function load() {
    try {
      const data = await getLiveEvents();
      setEvents(data);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();

    const timer = setInterval(load, 30000);

    return () => clearInterval(timer);
  }, []);

  if (loading) {
    return (
      <div className="py-20 text-center text-zinc-400">
        Loading live scores…
      </div>
    );
  }

  return (
    <section className="space-y-4">
      {events.length === 0 ? (
        <div className="rounded-2xl border border-zinc-800 p-8 text-center text-zinc-400">
          No live events right now.
        </div>
      ) : (
        events.map((event) => (
          <LiveMatchCard
            key={event.id}
            event={event}
          />
        ))
      )}
    </section>
  );
}
