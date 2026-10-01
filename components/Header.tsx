import Link from "next/link";

export default function Header() {
  return (
    <header className="sticky top-0 z-20 border-b border-zinc-800/80 bg-zinc-950/90 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4">
        <Link href="/" className="flex items-center gap-2">
          <span className="grid h-9 w-9 place-items-center rounded-xl bg-emerald-400 text-sm font-black text-zinc-950">
            SP
          </span>

          <div>
            <div className="font-black">Score Pulse</div>
            <div className="hidden text-[10px] uppercase tracking-widest text-zinc-500 sm:block">
              Every Sport. Every Score. Live.
            </div>
          </div>
        </Link>

        <Link
          href="/search"
          className="rounded-xl border border-zinc-800 px-3 py-2 text-sm text-zinc-300 hover:bg-zinc-900"
        >
          Search
        </Link>
      </div>
    </header>
  );
}
