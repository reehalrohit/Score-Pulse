import { NextResponse } from "next/server";
import { demoEvents } from "@/lib/demo-data";

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

  if (backend) {
    try {
      const response = await fetch(
        `${backend.replace(/\/$/, "")}/api/events/${encodeURIComponent(id)}`,
        {
          cache: "no-store",
        }
      );

      if (response.ok) {
        return NextResponse.json(await response.json());
      }
    } catch {}
  }

  const demo = demoEvents.find(
    (event) => event.id === id
  );

  if (!demo) {
    return NextResponse.json(
      {
        success: false,
        event: null,
      },
      { status: 404 }
    );
  }

  return NextResponse.json({
    success: true,
    source: "demo",
    event: demo,
  });
}
