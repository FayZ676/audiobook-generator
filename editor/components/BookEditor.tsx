"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { askClaude, changeSegment, saveCharacter } from "@/app/actions";
import type { Book, CastMember, LineRef, Segment, SegmentChange } from "@/lib/model";
import { applyChange, fixOrder, likelySpeakers, lineKey, nextId, readiness } from "@/lib/model";
import CastPanel from "./CastPanel";
import ControlBar from "./ControlBar";
import LinePanel from "./LinePanel";
import Prose from "./Prose";

/** Asking Claude Opus about lines, which happens only when a person asks. */
export type Claude = {
  /** Lines being asked about now, as lineKey(chapter, segment). */
  asking: Set<string>;
  askLines(chapterId: string, segmentIds: string[]): void;
  /** Every unreviewed line of the book, a chapter per request. */
  checkBook(): void;
  bookProgress: { done: number; total: number } | null;
};

type Selection = {
  chapter: string;
  segment: string;
  // Reached with N, so deciding moves on to the next; clicked, so it closes.
  stepping: boolean;
};
type Undo = { chapter: string; segment: string; before: SegmentChange };

/** The book, with quiet controls to find lines and fix who says them. Every
 * edit is saved to disk as it's made. */
export default function BookEditor({ initial }: { initial: Book }) {
  const [book, setBook] = useState(initial);
  const [selection, setSelection] = useState<Selection | null>(null);
  const [focusSpeaker, setFocusSpeaker] = useState<string | null>(null);
  const [castOpen, setCastOpen] = useState(false);
  const [undos, setUndos] = useState<Undo[]>([]);
  const [error, setError] = useState<string | null>(null);
  const searchRef = useRef<HTMLInputElement>(null);

  const report = (what: string) => (e: Error) => setError(`${what}: ${e.message}. Reload to see what's on disk.`);

  const changeLine = (chapterId: string, segmentId: string, change: SegmentChange) => {
    setBook((b) => ({
      ...b,
      chapters: b.chapters.map((c) =>
        c.id !== chapterId
          ? c
          : { ...c, segments: c.segments.map((s) => (s.id === segmentId ? applyChange(s, change, new Date().toISOString()) : s)) },
      ),
    }));
    changeSegment(book.name, chapterId, segmentId, change).catch(report("Couldn't save"));
  };

  const saveMember = (member: CastMember) => {
    setBook((b) => ({
      ...b,
      cast: b.cast.some((m) => m.id === member.id) ? b.cast.map((m) => (m.id === member.id ? member : m)) : [...b.cast, member],
    }));
    saveCharacter(book.name, member).catch(report("Couldn't save"));
  };

  // Claude Opus, only when asked.
  const [asking, setAsking] = useState<Set<string>>(new Set());
  const [bookProgress, setBookProgress] = useState<Claude["bookProgress"]>(null);
  const ask = async (chapterId: string, segmentIds: string[]) => {
    const keys = segmentIds.map((id) => lineKey(chapterId, id));
    setAsking((a) => new Set([...a, ...keys]));
    try {
      const answers = await askClaude(book.name, chapterId, segmentIds);
      setBook((b) => ({
        ...b,
        chapters: b.chapters.map((c) =>
          c.id !== chapterId
            ? c
            : { ...c, segments: c.segments.map((s) => (answers[s.id] ? { ...s, recheck_speaker_id: answers[s.id] } : s)) },
        ),
      }));
    } catch (e) {
      report("Couldn't ask Claude")(e as Error);
    } finally {
      setAsking((a) => new Set([...a].filter((k) => !keys.includes(k))));
    }
  };
  const claude: Claude = {
    asking,
    askLines: (chapterId, segmentIds) => void ask(chapterId, segmentIds),
    async checkBook() {
      const chapters = book.chapters.filter((c) => c.segments.some((s) => s.is_dialogue && !s.reviewed && !s.recheck_speaker_id));
      setBookProgress({ done: 0, total: chapters.length });
      for (const [i, c] of chapters.entries()) {
        await ask(c.id, []); // none named: every unreviewed line of the chapter
        setBookProgress({ done: i + 1, total: chapters.length });
      }
      setBookProgress(null);
    },
    bookProgress,
  };

  const ready = useMemo(() => readiness(book), [book]);
  const order = useMemo(() => fixOrder(book), [book]);
  const selected: LineRef | null = useMemo(() => {
    if (!selection) return null;
    const chapter = book.chapters.find((c) => c.id === selection.chapter);
    const index = chapter?.segments.findIndex((s) => s.id === selection.segment) ?? -1;
    return chapter && index >= 0 ? { chapter: chapter.id, index, segment: chapter.segments[index] } : null;
  }, [book, selection]);

  const scrollTo = (chapter: string, segmentId: string) =>
    requestAnimationFrame(() =>
      document.getElementById(`line-${chapter}-${segmentId}`)?.scrollIntoView({ block: "center", behavior: "smooth" }),
    );

  const select = (line: { chapter: string; segment: Segment }, stepping: boolean) => {
    setSelection({ chapter: line.chapter, segment: line.segment.id, stepping });
    scrollTo(line.chapter, line.segment.id);
  };

  const linesOf = (speaker: string) =>
    book.chapters.flatMap((c) =>
      c.segments.filter((s) => s.is_dialogue && s.speaker_id === speaker).map((segment) => ({ chapter: c.id, segment })),
    );

  /** N: the next line most likely wrong, or, finding one character, their next line. */
  const step = (by: 1 | -1) => {
    const isSelected = (l: { chapter: string; segment: Segment }) =>
      !!selected && l.chapter === selected.chapter && l.segment.id === selected.segment.id;
    const candidates = focusSpeaker ? linesOf(focusSpeaker) : order.filter((l) => !l.segment.reviewed || isSelected(l));
    if (!candidates.length) return;
    const at = candidates.findIndex(isSelected);
    select(candidates[(at + by + candidates.length) % candidates.length], true);
  };

  const decide = (speaker: string) => {
    if (!selected) return;
    const s = selected.segment;
    setUndos((u) => [...u.slice(-50), { chapter: selected.chapter, segment: s.id, before: { speaker_id: s.speaker_id, reviewed: s.reviewed } }]);
    changeLine(selected.chapter, s.id, { speaker_id: speaker, reviewed: true });
    if (selection?.stepping && !focusSpeaker) {
      // On to the next unchecked line most likely wrong, after this one.
      const at = order.findIndex((l) => l.chapter === selected.chapter && l.segment.id === s.id);
      const next = [...order.slice(at + 1), ...order.slice(0, Math.max(0, at))].find((l) => !l.segment.reviewed);
      if (next) select(next, true);
      else setSelection(null);
    } else setSelection(null);
  };

  const undo = () => {
    const last = undos.at(-1);
    if (!last) return;
    setUndos((u) => u.slice(0, -1));
    changeLine(last.chapter, last.segment, last.before);
    const segment = book.chapters.find((c) => c.id === last.chapter)?.segments.find((s) => s.id === last.segment);
    if (segment) select({ chapter: last.chapter, segment }, selection?.stepping ?? false);
  };

  const likely = useMemo(() => {
    if (!selected) return [];
    const chapter = book.chapters.find((c) => c.id === selected.chapter)!;
    const suggested = selected.segment.recheck_speaker_id;
    return [...new Set([...(suggested ? [suggested] : []), ...likelySpeakers(chapter, selected.index, book.cast)])];
  }, [book, selected]);

  /** A: take Claude's answer if it has one, else ask for it. */
  const useClaude = () => {
    if (!selected) return;
    const s = selected.segment;
    if (s.recheck_speaker_id) decide(s.recheck_speaker_id);
    else if (!asking.has(lineKey(selected.chapter, s.id))) claude.askLines(selected.chapter, [s.id]);
  };

  const addCharacter = (name: string) => {
    const member: CastMember = { id: nextId(book.cast), names: [name], age: "middle-aged", gender: "male", voice: null };
    saveMember(member);
    decide(member.id);
  };

  // Keys, with the latest handlers, without re-adding the listener every render.
  const keys = useRef<(e: KeyboardEvent) => void>(() => {});
  keys.current = (e) => {
    if (e.metaKey || e.ctrlKey || e.altKey || (e.target as HTMLElement).closest("input, textarea, select")) return;
    if (e.key === "Escape") {
      if (selection) setSelection(null);
      else if (castOpen) setCastOpen(false);
      else setFocusSpeaker(null);
    } else if (e.key === "n" || e.key === "j") step(1);
    else if (e.key === "N" || e.key === "p" || e.key === "k") step(-1);
    else if (e.key === "c") setCastOpen((o) => !o);
    else if (e.key === "z" || e.key === "u") undo();
    else if (!selected) return;
    else if (e.key === "Enter") decide(selected.segment.speaker_id);
    else if (/^[1-9]$/.test(e.key) && likely[Number(e.key) - 1]) decide(likely[Number(e.key) - 1]);
    else if (e.key === "/") searchRef.current?.focus();
    else if (e.key === "a") useClaude();
    else return;
    e.preventDefault();
  };
  useEffect(() => {
    const listener = (e: KeyboardEvent) => keys.current(e);
    window.addEventListener("keydown", listener);
    return () => window.removeEventListener("keydown", listener);
  }, []);

  // Stable per chapter, so a chapter that didn't change doesn't re-render.
  const pickIn = useCallback(
    (chapter: string) => (segment: Segment) => setSelection({ chapter, segment: segment.id, stepping: false }),
    [],
  );
  const pickers = useMemo(() => new Map(initial.chapters.map((c) => [c.id, pickIn(c.id)])), [initial.chapters, pickIn]);

  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-20 bg-bg/80 backdrop-blur">
        <div className="mx-auto flex h-12 max-w-3xl items-center gap-4 px-6 text-sm">
          <Link href="/" className="font-semibold capitalize tracking-tight">
            {book.name}
          </Link>
          <select
            value=""
            onChange={(e) => document.getElementById(`chapter-${e.target.value}`)?.scrollIntoView({ behavior: "smooth" })}
            className="ml-auto max-w-56 truncate rounded-md bg-transparent py-1 text-muted outline-none hover:text-ink"
          >
            <option value="" disabled>
              Go to chapter…
            </option>
            {book.chapters.map((c) => (
              <option key={c.id} value={c.id}>
                {c.title}
              </option>
            ))}
          </select>
        </div>
      </header>

      {error && (
        <p className="mx-auto mt-2 max-w-3xl rounded-md bg-red-500/10 px-4 py-2 text-sm text-red-600 dark:text-red-400">{error}</p>
      )}

      <main className="mx-auto max-w-3xl px-6 pb-[60vh] pt-10">
        {book.chapters.map((c) => (
          <section key={c.id} id={`chapter-${c.id}`} className="scroll-mt-16 border-t border-line pb-16 pt-12 first:border-0 first:pt-0">
            <Prose
              chapter={c.id}
              segments={c.segments}
              cast={book.cast}
              selected={selected?.chapter === c.id ? selected.segment.id : undefined}
              focusSpeaker={focusSpeaker}
              onPick={pickers.get(c.id)}
            />
          </section>
        ))}
      </main>

      <div className="pointer-events-none fixed inset-x-0 bottom-0 z-30 px-4 pb-5">
        <div className="pointer-events-auto">
          {selected ? (
            <LinePanel
              book={book}
              line={selected}
              likely={likely}
              asking={asking.has(lineKey(selected.chapter, selected.segment.id))}
              searchRef={searchRef}
              onPick={decide}
              onAdd={addCharacter}
              onClaude={useClaude}
              onClose={() => setSelection(null)}
            />
          ) : (
            <ControlBar
              book={book}
              ready={ready}
              claude={claude}
              focusSpeaker={focusSpeaker}
              onNext={() => step(1)}
              onClearFocus={() => setFocusSpeaker(null)}
              onCast={() => setCastOpen(true)}
            />
          )}
        </div>
      </div>

      {castOpen && (
        <CastPanel
          book={book}
          focused={focusSpeaker}
          onFocus={(id) => {
            setFocusSpeaker(id);
            setSelection(null);
            setCastOpen(false);
            const first = id ? linesOf(id)[0] : undefined;
            if (first) scrollTo(first.chapter, first.segment.id);
          }}
          onChange={saveMember}
          onClose={() => setCastOpen(false)}
        />
      )}
    </div>
  );
}
