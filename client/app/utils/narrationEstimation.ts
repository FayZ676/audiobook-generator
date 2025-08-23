import { Script } from "../actions/script";

export function countWords(text: string): number {
  return text.trim().split(/\s+/).filter(Boolean).length;
}

export function calculateWordCount(script: Script): number {
  return script.segments.reduce(
    (total, segment) => total + countWords(segment.text),
    0
  );
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
  console.log(`Word Count: ${wordCount}`);
  console.log(`Words Per Minute: ${wordsPerMinute}`);
  console.log(`Duration Base: ${durationBase}`);
  return Math.max(durationBase, Math.round((wordCount / wordsPerMinute) * 60));
}
