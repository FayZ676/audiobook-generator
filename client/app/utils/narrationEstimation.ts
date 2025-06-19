import { Script } from "../actions/script";

export function calculateWordCount(script: Script): number {
  return script.reduce((total, segment) => {
    return (
      total + segment.text.split(/\s+/).filter((word) => word.length > 0).length
    );
  }, 0);
}

export function estimateNarrationDuration(wordCount: number): number {
  // Based on: 4500 words = 30 minutes audio = 15 minutes generation time
  const wordsPerMinute = 4500 / 15; // 300 words per minute of generation time
  return Math.max(5, Math.round((wordCount / wordsPerMinute) * 60)); // At least 5 seconds, result in seconds
}
