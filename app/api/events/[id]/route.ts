import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function GET(
  _request: Request,
  {
    params,
  }: {
    params: Promise<{ id: string }>;
  }
) {
  const { id } = await params;
  const backend = process.env.SCOREPULSE_API_URL;

  if (!backend) {
    return NextResponse.json(
      {
        success: false,
        error: "SCOREPULSE_API_URL is not configured",
        event: null,
      },
      { status: 500 }
    );
  }

  try {
    const response = await fetch(
      `${backend.replace(/\/$/, "")}/api/events/${encodeURIComponent(id)}`,
      { cache: "no-store" }
    );

    const data = await response.json();

    return NextResponse.json(data, { status: response.status });
  } catch {
    return NextResponse.json(
      {
        success: false,
        error: "Event backend unavailable",
        event: null,
      },
      { status: 502 }
    );
  }
}
