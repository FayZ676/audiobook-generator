import { Script } from "../actions/script";

export function calculateWordCount(script: Script): number {
  return script.segments.reduce((total, segment) => {
    return (
      total + segment.text.split(/\s+/).filter((word) => word.length > 0).length
    );
  }, 0);
}

export function estimateNarrationDurationSeconds(wordCount: number): number {
  const wordsPerMinute = parseInt(
    process.env.NEXT_PUBLIC_NARRATION_WORDS_PER_MINUTE || "7",
    10
  );
  const durationBase = parseInt(
    process.env.NEXT_PUBLIC_NARRATION_DURATION_BASE || "30",
    10
  );
  return Math.max(durationBase, Math.round((wordCount / wordsPerMinute) * 60));
}
