import { LiveEvent } from "./types";

interface LiveResponse {
  success?: boolean;
  updatedAt?: string;
  events?: LiveEvent[];
}

export async function getLiveEvents(): Promise<LiveEvent[]> {
  const response = await fetch("/api/live", {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Unable to load live scores");
  }

  const data = (await response.json()) as LiveResponse;

  if (!Array.isArray(data.events)) {
    return [];
  }

  return data.events;
}
