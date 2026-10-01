import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function GET() {
  const backend = process.env.SCOREPULSE_API_URL;

  if (!backend) {
    return NextResponse.json(
      {
        success: false,
        error: "SCOREPULSE_API_URL is not configured",
        events: [],
      },
      { status: 500 }
    );
  }

  try {
    const response = await fetch(
      `${backend.replace(/\/$/, "")}/api/live`,
      { cache: "no-store" }
    );

    if (!response.ok) {
      return NextResponse.json(
        {
          success: false,
          error: `Backend returned ${response.status}`,
          events: [],
        },
        { status: 502 }
      );
    }

    return NextResponse.json(await response.json());
  } catch {
    return NextResponse.json(
      {
        success: false,
        error: "Live score backend unavailable",
        events: [],
      },
      { status: 502 }
    );
  }
}
