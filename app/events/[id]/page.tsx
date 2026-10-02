import Link from "next/link";

interface EventPageProps { params: Promise<{ id: string }> }

interface EventResponse {
  success: boolean;
  event?: {
    id: string;
    sport: string;
    status: string;
    startTime: string;
    league: { name: string; country?: string };
    home: { name: string; shortName?: string; logo?: string };
    away: { name: string; shortName?: string; logo?: string };
    score?: { home: string | number; away: string | number; period?: string };
    venue?: string;
    broadcast?: string;
  } | null;
}

async function getEvent(id: string): Promise<EventResponse> {
  const base = process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000";
  try {
    const response = await fetch(`${base}/api/events/${encodeURIComponent(id)}`, { cache: "no-store" });
    if (!response.ok) return { success: false, event: null };
    return response.json();
  } catch {
    return { success: false, event: null };
  }
}

export default async function EventPage({ params }: EventPageProps) {
  const { id } = await params;
  const result = await getEvent(id);
  const event = result.event;

  if (!event) {
    return (
      <main className="mx-auto max-w-4xl px-4 py-12">
        <Link href="/" className="text-sm text-emerald-400">← Back to scores</Link>
        <div className="mt-8 rounded-3xl border border-zinc-800 bg-zinc-950 p-8">
          <h1 className="text-2xl font-black">Match not found</h1>
          <p className="mt-2 text-sm text-zinc-500">This event may have ended or is temporarily unavailable.</p>
        </div>
      </main>
    );
  }

  const isLive = event.status === "live" || event.status === "halftime";
  const isGolf = event.sport === "golf";

  return (
    <main className="mx-auto max-w-4xl px-4 py-8">
      <Link href="/" className="text-sm text-emerald-400">← Live scores</Link>

      <section className="mt-6 overflow-hidden rounded-3xl border border-zinc-800 bg-zinc-950">
        <div className="border-b border-zinc-800 px-5 py-4 text-center">
          <p className="text-xs uppercase tracking-widest text-zinc-500">{event.sport}</p>
          <h1 className="mt-1 font-bold">{event.league.name}</h1>
          {event.league.country && <p className="mt-1 text-xs text-zinc-600">{event.league.country}</p>}
        </div>

        <div className="p-6 sm:p-10">
          <div className="flex justify-center">
            {isLive ? (
              <span className="flex items-center gap-2 rounded-full bg-red-500/10 px-4 py-2 text-xs font-bold text-red-400">
                <span className="h-2 w-2 animate-pulse rounded-full bg-red-500" />LIVE
              </span>
            ) : (
              <span className="rounded-full bg-zinc-900 px-4 py-2 text-xs font-bold uppercase text-zinc-400">{event.status}</span>
            )}
          </div>

          {isGolf ? (
            <div className="mt-10 rounded-2xl border border-zinc-800 bg-zinc-900/40 p-6 text-center">
              <div className="text-4xl">⛳</div>
              <h2 className="mt-3 text-2xl font-black">Golf tournament</h2>
              <p className="mt-1 text-zinc-400">{event.league.name}</p>
              {event.startTime && <p className="mt-4 text-sm text-zinc-500">Start: {new Date(event.startTime).toLocaleString()}</p>}
              <p className="mt-5 text-sm text-zinc-500">
                Tournament leaderboard and player scoring are handled separately from team-based match scoring.
              </p>
            </div>
          ) : (
            <div className="mt-10 grid grid-cols-[1fr_auto_1fr] items-center gap-4">
              <Team name={event.home.name} shortName={event.home.shortName} score={event.score?.home} />
              <div className="text-center"><span className="text-xs text-zinc-600">{event.score?.period || "VS"}</span></div>
              <Team name={event.away.name} shortName={event.away.shortName} score={event.score?.away} align="right" />
            </div>
          )}
        </div>

        {(event.venue || event.broadcast) && (
          <div className="grid gap-3 border-t border-zinc-800 p-5 sm:grid-cols-2">
            {event.venue && <div><p className="text-[10px] uppercase tracking-widest text-zinc-600">Venue</p><p className="mt-1 text-sm text-zinc-300">{event.venue}</p></div>}
            {event.broadcast && <div><p className="text-[10px] uppercase tracking-widest text-zinc-600">Broadcast</p><p className="mt-1 text-sm text-zinc-300">{event.broadcast}</p></div>}
          </div>
        )}
      </section>

      <section className="mt-6 rounded-3xl border border-zinc-800 bg-zinc-950 p-6">
        <h2 className="text-lg font-bold">{isGolf ? "Tournament Centre" : "Match Centre"}</h2>
        <p className="mt-2 text-sm text-zinc-500">
          {isGolf ? "Detailed leaderboard and player scoring can be added here." : "Detailed statistics, timeline and sport-specific scorecards will appear here."}
        </p>
      </section>
    </main>
  );
}

function Team({ name, shortName, score, align = "left" }: {
  name: string; shortName?: string; score?: string | number; align?: "left" | "right";
}) {
  return (
    <div className={align === "right" ? "text-right" : "text-left"}>
      <p className="text-lg font-bold sm:text-xl">{name}</p>
      {shortName && <p className="mt-1 text-xs text-zinc-500">{shortName}</p>}
      <p className="mt-4 text-4xl font-black sm:text-5xl">{score ?? "-"}</p>
    </div>
  );
}
