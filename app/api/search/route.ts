import { NextResponse } from "next/server";
import { demoEvents } from "@/lib/demo-data";

export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  const url = new URL(request.url);
  const query =
    url.searchParams.get("q")?.trim().toLowerCase() || "";

  if (!query) {
    return NextResponse.json({
      success: true,
      results: [],
    });
  }

  const results = demoEvents.filter((event) =>
    [
      event.home.name,
      event.home.shortName,
      event.away.name,
      event.away.shortName,
      event.league.name,
      event.sport,
    ]
      .filter(Boolean)
      .join(" ")
      .toLowerCase()
      .includes(query)
  );

  return NextResponse.json({
    success: true,
    results,
  });
}
    results,
  });
}
