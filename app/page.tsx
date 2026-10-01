import ScorePulseDashboard from "@/components/ScorePulseDashboard";
import SportNav from "@/components/SportNav";

export default function Home() {
  return (
    <main className="mx-auto min-h-screen max-w-6xl px-4 py-8">
      <header className="mb-8">
        <p className="mb-2 text-sm font-semibold uppercase tracking-widest text-emerald-400">
          Score Pulse
        </p>

        <h1 className="text-4xl font-black tracking-tight sm:text-5xl">
          Every Sport.
          <br />
          Every Score. Live.
        </h1>

        <p className="mt-4 max-w-xl text-zinc-400">
          Live scores, fixtures, standings and match information
          across the world's biggest sports.
        </p>
      </header>

      <div className="mb-8">
        <SportNav />
      </div>

      <div className="mb-5 flex items-center justify-between">
        <h2 className="text-xl font-bold">
          Live Now
        </h2>

        <span className="text-xs text-zinc-500">
          Auto-refresh · 30s
        </span>
      </div>

      <ScorePulseDashboard />
    </main>
  );
}
