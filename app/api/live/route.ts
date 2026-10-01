import { NextResponse } from "next/server";
import { demoEvents } from "@/lib/demo-data";

export const dynamic = "force-dynamic";

export async function GET() {
  const backend = process.env.SCOREPULSE_API_URL;

  if (backend) {
    try {
      const response = await fetch(
        `${backend.replace(/\/$/, "")}/api/live`,
        { cache: "no-store" }
      );

      if (response.ok) {
        return NextResponse.json(await response.json());
      }
    } catch {}
  }

  return NextResponse.json({
    success: true,
    source: "demo",
    updatedAt: new Date().toISOString(),
    events: demoEvents,
  });
}
