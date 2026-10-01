import Link from "next/link";
import { demoEvents } from "@/lib/demo-data";

export default async function EventPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  const event = demoEvents.find((item) => item.id === id);

  if (!event) {
    return (
      <main className="mx-auto max-w-3xl px-4 py-16">
        <Link href="/" className="text-emerald-400">
          ← Back
        </Link>

        <h1 className="mt-8 text-3xl font-black">
          Event not found
        </h1>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-3xl px-4 py-8">
      <Link href="/" className="text-sm text-emerald-400">
        ← Live scores
      </Link>

      <section className="mt-6 rounded-3xl border border-zinc-800 bg-zinc-950 p-6">
        <div className="text-center text-sm text-zinc-500">
          {event.league.name}
        </div>

        <div className="mt-8 grid grid-cols-[1fr_auto_1fr] items-center gap-4 text-center">
          <div>
            <div className="font-bold">{event.home.name}</div>
            <div className="mt-2 text-4xl font-black">
              {event.score?.home ?? "-"}
            </div>
          </div>

          <div>
            <div className="rounded-full bg-red-500/10 px-3 py-1 text-xs font-bold text-red-400">
              {event.status.toUpperCase()}
            </div>

            <div className="mt-2 text-xs text-zinc-500">
              {event.score?.period}
            </div>
          </div>

          <div>
            <div className="font-bold">{event.away.name}</div>
            <div className="mt-2 text-4xl font-black">
              {event.score?.away ?? "-"}
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
