import { NextRequest, NextResponse } from 'next/server';

/**
 * API route handler for fetching narration URLs
 */
export async function GET(
  request: NextRequest,
  { params }: { params: { filename: string } }
) {
  try {
    const filename = params.filename;
    const response = await fetch(
      `${process.env.AUDIOBOOK_SERVICE_URL}/narration/${filename}`
    );
    
    if (!response.ok) {
      return new NextResponse(JSON.stringify(null), {
        status: response.status,
        headers: { 'Content-Type': 'application/json' },
      });
    }
    
    const narrationUrl = await response.json();
    return NextResponse.json(narrationUrl);
  } catch (error) {
    console.error('Error fetching narration:', error);
    return new NextResponse(JSON.stringify(null), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
}