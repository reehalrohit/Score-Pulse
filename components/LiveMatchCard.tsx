"use client";

import Link from "next/link";
import { LiveEvent } from "@/lib/types";

export default function LiveMatchCard({
  event,
}: {
  event: LiveEvent;
}) {
  const live =
    event.status === "live" ||
    event.status === "halftime";

  const statusLabel =
    event.status === "live"
      ? "LIVE"
      : event.status === "halftime"
        ? "HALF TIME"
        : event.status.toUpperCase();

  return (
    <Link
      href={`/events/${encodeURIComponent(event.id)}`}
      className="block rounded-2xl border border-zinc-800 bg-zinc-950 p-4 transition hover:border-zinc-600 hover:bg-zinc-900"
    >
      <div className="mb-4 flex items-center justify-between gap-3">
        <div className="min-w-0">
          <p className="truncate text-xs text-zinc-400">
            {event.league.name}
          </p>

          <p className="mt-1 text-[11px] uppercase tracking-wider text-zinc-600">
            {event.sport}
          </p>
        </div>

        {live ? (
          <span className="flex shrink-0 items-center gap-1.5 text-xs font-semibold text-red-400">
            <span className="h-2 w-2 animate-pulse rounded-full bg-red-500" />
            {statusLabel}
          </span>
        ) : (
          <span className="shrink-0 text-xs text-zinc-500">
            {statusLabel}
          </span>
        )}
      </div>

      <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-3">
        <div className="min-w-0">
          <p className="truncate font-semibold">
            {event.home.name}
          </p>

          {event.home.shortName && (
            <p className="mt-1 text-xs text-zinc-500">
              {event.home.shortName}
            </p>
          )}
        </div>

        <div className="min-w-[60px] text-center">
          <p className="text-xl font-bold">
            {event.score?.home ?? "-"}
          </p>

          <p className="my-1 text-[11px] text-zinc-500">
            {event.score?.period ?? "vs"}
          </p>

          <p className="text-xl font-bold">
            {event.score?.away ?? "-"}
          </p>
        </div>

        <div className="min-w-0 text-right">
          <p className="truncate font-semibold">
            {event.away.name}
          </p>

          {event.away.shortName && (
            <p className="mt-1 text-xs text-zinc-500">
              {event.away.shortName}
            </p>
          )}
        </div>
      </div>
    </Link>
  );
          }
