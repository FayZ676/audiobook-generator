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

// Confirming this many lines in a row without a correction means the rest,
// which the model is surer of, are very likely right.
export const READY_AFTER = 20;

export type Readiness = {
  reviewed: number;
  corrected: number;
  confirmedInARow: number; // most recent reviews with no correction
  ready: boolean;
};

export function readiness(book: Book): Readiness {
  const reviewed = book.chapters
    .flatMap((c) => c.segments)
    .filter((s) => s.is_dialogue && s.reviewed)
    .sort((a, b) => (b.reviewed_at ?? "").localeCompare(a.reviewed_at ?? ""));
  const firstFix = reviewed.findIndex(wasCorrected);
  const confirmedInARow = firstFix === -1 ? reviewed.length : firstFix;
  return {
    reviewed: reviewed.length,
    corrected: reviewed.filter(wasCorrected).length,
    confirmedInARow,
    ready: confirmedInARow >= READY_AFTER,
  };
}

export type Chapter = { id: string; title: string; segments: Segment[] };

export type Book = { name: string; cast: CastMember[]; chapters: Chapter[] };

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
