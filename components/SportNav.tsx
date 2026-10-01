"use client";

import { sports } from "@/lib/sports";

export default function SportNav() {
  return (
    <nav className="flex gap-2 overflow-x-auto pb-2 scrollbar-none">
      {sports.map((sport, i) => (
        <button
          key={sport.id}
          className={`flex shrink-0 items-center gap-2 rounded-full border px-4 py-2 text-sm transition ${
            i === 0
              ? "border-emerald-400/40 bg-emerald-400/10 text-emerald-300"
              : "border-zinc-800 bg-zinc-950 text-zinc-300 hover:border-zinc-600"
          }`}
        >
          <span>{sport.emoji}</span>
          {sport.name}
        </button>
      ))}
    </nav>
  );
}
