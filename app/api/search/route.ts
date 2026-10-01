import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  const url = new URL(request.url);
  const query = url.searchParams.get("q")?.trim() || "";
  const backend = process.env.SCOREPULSE_API_URL;

  if (!backend) {
    return NextResponse.json(
      {
        success: false,
        error: "SCOREPULSE_API_URL is not configured",
        results: [],
      },
      { status: 500 }
    );
  }

  if (!query) {
    return NextResponse.json({
      success: true,
      results: [],
    });
  }

  try {
    const response = await fetch(
      `${backend.replace(/\/$/, "")}/api/search?q=${encodeURIComponent(query)}`,
      { cache: "no-store" }
    );

    if (!response.ok) {
      return NextResponse.json(
        {
          success: false,
          error: `Backend returned ${response.status}`,
          results: [],
        },
        { status: 502 }
      );
    }

    return NextResponse.json(await response.json());
  } catch {
    return NextResponse.json(
      {
        success: false,
        error: "Search backend unavailable",
        results: [],
      },
      { status: 502 }
    );
  }
}
