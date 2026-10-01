"use client";

import { LiveEvent } from "@/lib/types";
import Link from "next/link";

export default function LiveMatchCard({
  event
}: {
  event: LiveEvent;
}) {
  const live =
    event.status === "live" ||
    event.status === "halftime";

  return (
    <Link
      href={`/events/${event.id}`}
      className="block rounded-2xl border border-zinc-800 bg-zinc-950 p-4 transition hover:border-zinc-600"
    >
      <div className="mb-3 flex items-center justify-between">
        <span className="text-xs text-zinc-400">
          {event.league.name}
        </span>

        {live && (
          <span className="flex items-center gap-1 text-xs font-semibold text-red-400">
            <span className="h-2 w-2 animate-pulse rounded-full bg-red-500" />
            LIVE
          </span>
        )}
      </div>

      <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-3">
        <div>
          <p className="font-semibold">{event.home.name}</p>
          <p className="mt-1 text-xs text-zinc-500">
            {event.home.shortName}
          </p>
        </div>

        <div className="text-center">
          <p className="text-xl font-bold">
            {event.score?.home ?? "-"}
          </p>
          <p className="text-xs text-zinc-500">
            {event.score?.period ?? "vs"}
          </p>
          <p className="text-xl font-bold">
            {event.score?.away ?? "-"}
          </p>
        </div>

        <div className="text-right">
          <p className="font-semibold">{event.away.name}</p>
          <p className="mt-1 text-xs text-zinc-500">
            {event.away.shortName}
          </p>
        </div>
      </div>
    </Link>
  );
}
