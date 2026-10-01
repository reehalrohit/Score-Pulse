import Link from "next/link";
import { sports } from "@/lib/sports";

export default function SportNav({
  activeSport = "all",
}: {
  activeSport?: string;
}) {
  return (
    <nav className="flex gap-2 overflow-x-auto pb-2 scrollbar-none">
      {sports.map((sport) => {
        const active = activeSport === sport.id;

        const href =
          sport.id === "all"
            ? "/"
            : `/?sport=${encodeURIComponent(sport.id)}`;

        return (
          <Link
            key={sport.id}
            href={href}
            className={`flex shrink-0 items-center gap-2 rounded-full border px-4 py-2 text-sm transition ${
              active
                ? "border-emerald-400/40 bg-emerald-400/10 text-emerald-300"
                : "border-zinc-800 bg-zinc-950 text-zinc-300 hover:border-zinc-600 hover:bg-zinc-900"
            }`}
          >
            <span>{sport.emoji}</span>
            {sport.name}
          </Link>
        );
      })}
    </nav>
  );
}
