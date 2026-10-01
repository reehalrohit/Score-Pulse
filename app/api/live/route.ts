import { NextResponse } from "next/server";
import { demoEvents } from "@/lib/demo-data";

export async function GET() {
  const backend = process.env.SCOREPULSE_API_URL;

  if (backend) {
    try {
      const response = await fetch(`${backend}/api/live`, {
        next: { revalidate: 15 }
      });

      if (response.ok) {
        const data = await response.json();
        return NextResponse.json(data);
      }
    } catch {
      // Fall back to demo data.
    }
  }

  return NextResponse.json({
    success: true,
    source: "demo",
    updatedAt: new Date().toISOString(),
    events: demoEvents
  });
}
