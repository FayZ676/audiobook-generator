'use client';

/**
 * Client-side function to check if narration exists without loading the full URL
 */
export async function checkNarrationExistsClient(userId: string): Promise<boolean> {
  try {
    const filename = `${userId}.mp3`;
    const response = await fetch(`/api/narration/${filename}/exists`);
    
    if (!response.ok) {
      return false;
    }
    
    const exists = await response.json();
    return exists;
  } catch (error) {
    console.error("Error checking narration existence:", error);
    return false;
  }
}