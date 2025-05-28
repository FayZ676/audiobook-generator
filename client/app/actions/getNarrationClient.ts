'use client';

/**
 * Client-side function to fetch the narration URL when needed
 * This follows Next.js recommendations for fetching data in client components
 */
export async function getNarrationClient(userId: string): Promise<string | null> {
  try {
    const filename = `${userId}.mp3`;
    const response = await fetch(`/api/narration/${filename}`);
    
    if (!response.ok) {
      console.error(`Failed to fetch narration: ${response.status} ${response.statusText}`);
      return null;
    }
    
    const narrationUrl = await response.json();
    return narrationUrl;
  } catch (error) {
    console.error("Error fetching narration:", error);
    return null;
  }
}