// Mirrors tta_script/cast.py and tta_script/script.py, which write these files.

export const NARRATOR_ID = "narrator";
export const AGES = ["young", "middle-aged", "old"] as const;
export const GENDERS = ["male", "female"] as const;

export type CastMember = {
  id: string;
  names: string[]; // the first is the one shown
  age: (typeof AGES)[number];
  gender: (typeof GENDERS)[number];
  voice: string | null; // null until a person picks one
};

export type Segment = {
  id: string;
  text: string;
  speaker_id: string;
  is_dialogue: boolean;
  paragraph: number;
  confidence: number | null;
  reviewed: boolean;
  model_speaker_id?: string | null; // the model's speaker, kept once a person changes it
  reviewed_at?: string | null;
  recheck_speaker_id?: string | null; // Claude Opus's answer, when a person asked for it
};

export type SegmentChange = Partial<Pick<Segment, "speaker_id" | "reviewed">>;

/** A person's edit to a line. Changing the speaker keeps the model's
 * original, so a correction can be told apart from a confirmation. */
export function applyChange(segment: Segment, change: SegmentChange, now: string): Segment {
  const next = { ...segment };
  if (change.speaker_id !== undefined && change.speaker_id !== segment.speaker_id) {
    next.model_speaker_id ??= segment.speaker_id;
    next.speaker_id = change.speaker_id;
  }
  if (change.reviewed !== undefined) {
    next.reviewed = change.reviewed;
    next.reviewed_at = change.reviewed ? now : null;
  }
  return next;
}

export function wasCorrected(segment: Segment): boolean {
  return segment.model_speaker_id != null && segment.model_speaker_id !== segment.speaker_id;
}

/** What Claude Opus said about a line, if it was asked. */
export function opinion(segment: Segment): "agrees" | "disagrees" | null {
  if (!segment.recheck_speaker_id) return null;
  return segment.recheck_speaker_id === segment.speaker_id ? "agrees" : "disagrees";
}

/** Lines a person still needs to look at: not reviewed, and not already
 * confirmed by Claude Opus agreeing with the first answer. */
export function needsLook(segment: Segment): boolean {
  return segment.is_dialogue && !segment.reviewed && opinion(segment) !== "agrees";
}

// Confirming this many lines in a row without a correction means the rest,
// which the model is surer of, are very likely right.
export const READY_AFTER = 20;

export type Readiness = {
  reviewed: number;
  corrected: number;
  confirmedInARow: number; // most recent reviews with no correction
  disagreements: number; // lines Claude Opus disagreed on, still to look at
  unchecked: number; // dialogue lines neither reviewed nor checked by Claude Opus
  ready: boolean;
};

export function readiness(book: Book): Readiness {
  const lines = book.chapters.flatMap((c) => c.segments).filter((s) => s.is_dialogue);
  const reviewed = lines
    .filter((s) => s.reviewed)
    .sort((a, b) => (b.reviewed_at ?? "").localeCompare(a.reviewed_at ?? ""));
  const firstFix = reviewed.findIndex(wasCorrected);
  const confirmedInARow = firstFix === -1 ? reviewed.length : firstFix;
  const disagreements = lines.filter((s) => !s.reviewed && opinion(s) === "disagrees").length;
  const unchecked = lines.filter((s) => !s.reviewed && opinion(s) === null).length;
  return {
    reviewed: reviewed.length,
    corrected: reviewed.filter(wasCorrected).length,
    confirmedInARow,
    disagreements,
    unchecked,
    // Every line checked by someone, or enough right in a row that the rest likely are.
    ready: disagreements === 0 && (unchecked === 0 || confirmedInARow >= READY_AFTER),
  };
}

// Claude Opus 5.5 list prices per token, for estimates shown before asking.
const OPUS_INPUT = 4 / 1e6;
const OPUS_OUTPUT = 20 / 1e6;

/** Roughly what asking Claude Opus about these chapters' unchecked lines
 * costs: each chapter is read once, and each line answered briefly. Measured
 * on the eval books: about 0.6 input tokens per character of chapter (with
 * instructions), and 20 output tokens per line asked about. */
export function recheckCost(chapters: Chapter[]): number {
  return chapters.reduce((total, c) => {
    const lines = c.segments.filter((s) => s.is_dialogue && !s.reviewed && !s.recheck_speaker_id).length;
    if (!lines) return total;
    const chars = c.segments.reduce((n, s) => n + s.text.length, 0);
    return total + chars * 0.6 * OPUS_INPUT + (300 + lines * 20) * OPUS_OUTPUT;
  }, 0);
}

export type Chapter = { id: string; title: string; segments: Segment[] };

export type Book = { name: string; cast: CastMember[]; chapters: Chapter[] };

/** "CHAPTER I. Down the Rabbit-Hole" → { label: "CHAPTER I", name: "Down the Rabbit-Hole" }. */
export function splitTitle(text: string): { label: string | null; name: string } {
  const parts = /^((?:chapter|book|part)\s+\w+)[.:]?\s+(.+)$/i.exec(text);
  return parts ? { label: parts[1], name: parts[2] } : { label: null, name: text };
}

export function displayName(cast: CastMember[], id: string): string {
  return cast.find((m) => m.id === id)?.names[0] ?? id;
}

/** A new character id: c1, c2, ... never reusing a number (as cast.py does). */
export function nextId(cast: CastMember[]): string {
  const numbers = cast.map((m) => /^c(\d+)$/.exec(m.id)).map((m) => (m ? Number(m[1]) : 0));
  return `c${Math.max(0, ...numbers) + 1}`;
}

/** A steady hue per character, so each one is the same colour everywhere.
 * Ids are numbered in order of appearance (c1, c2, ...); stepping by the
 * golden angle keeps characters introduced together far apart in colour. */
export function speakerHue(id: string): number | null {
  if (id === NARRATOR_ID) return null;
  const n = Number(/^c(\d+)$/.exec(id)?.[1] ?? [...id].reduce((h, c) => h * 31 + c.charCodeAt(0), 0));
  return (n * 137.508) % 360;
}

/** Characters likely to have said a line: who speaks nearby, and who the
 * nearby narration names ("said the Gryphon"), closest first, then the
 * narrator. */
export function likelySpeakers(chapter: Chapter, index: number, cast: CastMember[], limit = 7): string[] {
  const window = 12;
  const scores = new Map<string, number>();
  const add = (id: string, score: number) => scores.set(id, Math.max(scores.get(id) ?? 0, score));
  const lo = Math.max(0, index - window);
  const hi = Math.min(chapter.segments.length, index + window + 1);
  for (let i = lo; i < hi; i++) {
    const s = chapter.segments[i];
    const closeness = window + 1 - Math.abs(i - index);
    if (s.is_dialogue && s.speaker_id !== NARRATOR_ID) add(s.speaker_id, closeness);
    if (!s.is_dialogue && Math.abs(i - index) <= 3) {
      for (const m of cast) {
        if (m.id !== NARRATOR_ID && m.names.some((n) => mentions(s.text, n))) add(m.id, closeness + 2);
      }
    }
  }
  const current = chapter.segments[index].speaker_id;
  scores.delete(current);
  const ranked = [...scores.entries()].sort((a, b) => b[1] - a[1]).map(([id]) => id);
  return [current, ...ranked.slice(0, limit - 2), NARRATOR_ID].filter(
    (id, i, all) => all.indexOf(id) === i,
  );
}

function mentions(text: string, name: string): boolean {
  const bare = name.replace(/^the /i, "");
  return new RegExp(`\\b${bare.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}\\b`, "i").test(text);
}

/** A line of dialogue and where it is. */
export type LineRef = { chapter: string; index: number; segment: Segment };

export function lineKey(chapter: string, segmentId: string): string {
  return `${chapter}/${segmentId}`;
}

/** Claude Opus disagreed with the models' first answer (not the person's). */
export function claudeDisagreed(segment: Segment): boolean {
  const first = segment.model_speaker_id ?? segment.speaker_id;
  return !!segment.recheck_speaker_id && segment.recheck_speaker_id !== first;
}

// Below this confidence an unchecked line is marked as worth a look.
export const UNSURE_BELOW = 0.8;

/** How a line is marked in the text, if at all. */
export function mark(segment: Segment): "disagrees" | "unsure" | "fixed" | null {
  if (!segment.is_dialogue) return null;
  if (segment.reviewed) return wasCorrected(segment) ? "fixed" : null;
  if (opinion(segment) === "disagrees") return "disagrees";
  if (opinion(segment) === null && (segment.confidence ?? 0) < UNSURE_BELOW) return "unsure";
  return null;
}

/** Lines most likely wrong first: those Claude Opus disagreed with, then
 * the least confident. The order depends only on what the models said, so
 * checking a line never moves it. */
export function fixOrder(book: Book): LineRef[] {
  const lines: LineRef[] = [];
  for (const c of book.chapters)
    c.segments.forEach((segment, index) => {
      if (segment.reviewed || needsLook(segment)) lines.push({ chapter: c.id, index, segment });
    });
  return lines.sort(
    (a, b) =>
      Number(claudeDisagreed(b.segment)) - Number(claudeDisagreed(a.segment)) ||
      (a.segment.confidence ?? -1) - (b.segment.confidence ?? -1),
  );
}
