import { LiveEvent } from "./types";

export async function getLiveEvents(): Promise<LiveEvent[]> {
  const response = await fetch("/api/live", {
    cache: "no-store"
  });

  if (!response.ok) {
    throw new Error("Unable to load live scores");
  }

  const data = await response.json();
  return data.events ?? [];
}
