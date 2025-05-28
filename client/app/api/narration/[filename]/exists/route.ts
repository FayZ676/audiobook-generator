import { NextRequest, NextResponse } from 'next/server';

/**
 * API route handler for checking if narration exists without fetching the full URL
 */
export async function GET(
  request: NextRequest,
  { params }: { params: { filename: string } }
) {
  try {
    const filename = params.filename;
    const response = await fetch(
      `${process.env.AUDIOBOOK_SERVICE_URL}/narration/${filename}/exists`
    );
    
    if (!response.ok) {
      return NextResponse.json(false);
    }
    
    const exists = await response.json();
    return NextResponse.json(exists);
  } catch (error) {
    console.error('Error checking narration existence:', error);
    return NextResponse.json(false);
  }
}