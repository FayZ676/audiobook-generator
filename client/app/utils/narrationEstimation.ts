import { Script } from "../actions/script";

export function calculateWordCount(script: Script): number {
  return script.segments.reduce((total, segment) => {
    return (
      total + segment.text.split(/\s+/).filter((word) => word.length > 0).length
    );
  }, 0);
}

export function estimateNarrationDuration(wordCount: number): number {
  const wordsPerMinute = parseInt(
    process.env.NEXT_PUBLIC_NARRATION_WORDS_PER_MINUTE || "300",
    10
  );
  return Math.max(5, Math.round((wordCount / wordsPerMinute) * 60)); // At least 5 seconds, result in seconds
}
