import { auth } from "@clerk/nextjs/server";
import { NextResponse } from "next/server";

export async function GET() {
  const { userId } = await auth();
  if (!userId) {
    return NextResponse.json({ error: "User not authenticated" }, { status: 401 });
  }

  const filename = `${userId}.mp3`;
  try {
    const response = await fetch(
      `${process.env.AUDIOBOOK_SERVICE_URL}/narration/${filename}`
    );
    
    if (!response.ok) {
      return NextResponse.json({ error: "Narration not found" }, { status: response.status });
    }
    
    const narrationUrl = await response.json();
    return NextResponse.json(narrationUrl);
  } catch (error) {
    console.error("Error fetching narration:", error);
    return NextResponse.json({ error: "Failed to fetch narration" }, { status: 500 });
  }
}