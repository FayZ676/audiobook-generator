"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { askClaude, changeSegment, saveCharacter } from "@/app/actions";
import type { Book, CastMember, SegmentChange } from "@/lib/model";
import { applyChange, nextId, readiness } from "@/lib/model";
import CastView from "./CastView";
import ReadView from "./ReadView";
import FixView, { type FixBatch } from "./FixView";
import Overview from "./Overview";

export type Edits = {
  changeSegment(chapterId: string, segmentId: string, change: SegmentChange): void;
  saveCharacter(member: CastMember): void;
  /** Adds a character by name, with voice traits to fix in the cast later. */
  addCharacter(name: string): CastMember;
};

/** Asking Claude Opus about lines, which happens only when a person asks. */
export type Claude = {
  /** Lines being asked about now, as "chapter/segment". */
  asking: Set<string>;
  askLines(chapterId: string, segmentIds: string[]): void;
  /** Every unreviewed line of the book, a chapter per request. */
  checkBook(): void;
  bookProgress: { done: number; total: number } | null;
};

const VIEWS = ["Overview", "Cast", "Fix", "Read"] as const;
export type View = (typeof VIEWS)[number];
const TAB_LABELS: Record<View, string> = { Overview: "Overview", Cast: "Cast", Fix: "Fix lines", Read: "Read" };

/** Holds the book in memory and saves every edit to disk as it's made. */
export default function BookEditor({ initial, initialView }: { initial: Book; initialView?: string }) {
  const [book, setBook] = useState(initial);
  const [view, setViewState] = useState<View>(
    VIEWS.find((v) => v.toLowerCase() === initialView) ?? "Overview",
  );
  const setView = (v: View) => {
    setViewState(v);
    window.history.replaceState(null, "", `?view=${v.toLowerCase()}`); // a reload keeps the view
  };
  const [readAt, setReadAt] = useState<{ chapter: string; segment?: string }>({
    chapter: initial.chapters[0]?.id ?? "",
  });
  const [error, setError] = useState<string | null>(null);

  // The Fix lines batch outlives the view, and a reload (kept in this browser).
  const batchKey = `fix-batch:${initial.name}`;
  const [fixBatch, setFixBatchState] = useState<FixBatch | null>(null);
  const [loaded, setLoaded] = useState(false);
  useEffect(() => {
    try {
      const stored = localStorage.getItem(batchKey);
      if (stored) setFixBatchState(JSON.parse(stored));
    } catch {
      // No storage (private window, blocked site data): the batch lasts until reload.
    }
    setLoaded(true);
  }, [batchKey]);
  const setFixBatch = useCallback(
    (batch: FixBatch) => {
      setFixBatchState(batch);
      try {
        localStorage.setItem(batchKey, JSON.stringify(batch));
      } catch {
        // As above: kept in memory only.
      }
    },
    [batchKey],
  );

  const save = (write: Promise<void>) =>
    write.catch((e: Error) => setError(`Couldn't save: ${e.message}. Reload to see what's on disk.`));

  const edits: Edits = {
    changeSegment(chapterId, segmentId, change) {
      setBook((b) => ({
        ...b,
        chapters: b.chapters.map((c) =>
          c.id !== chapterId
            ? c
            : {
                ...c,
                segments: c.segments.map((s) => (s.id === segmentId ? applyChange(s, change, new Date().toISOString()) : s)),
              },
        ),
      }));
      save(changeSegment(book.name, chapterId, segmentId, change));
    },
    saveCharacter(member) {
      setBook((b) => ({ ...b, cast: b.cast.map((m) => (m.id === member.id ? member : m)) }));
      save(saveCharacter(book.name, member));
    },
    addCharacter(name) {
      const member: CastMember = { id: nextId(book.cast), names: [name], age: "middle-aged", gender: "male", voice: null };
      setBook((b) => ({ ...b, cast: [...b.cast, member] }));
      save(saveCharacter(book.name, member));
      return member;
    },
  };

  const [asking, setAsking] = useState<Set<string>>(new Set());
  const [bookProgress, setBookProgress] = useState<Claude["bookProgress"]>(null);

  const ask = async (chapterId: string, segmentIds: string[]) => {
    const keys = segmentIds.map((id) => `${chapterId}/${id}`);
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
      setError(`Couldn't ask Claude: ${(e as Error).message}`);
    } finally {
      setAsking((a) => new Set([...a].filter((k) => !keys.includes(k))));
    }
  };

  const claude: Claude = {
    asking,
    askLines: (chapterId, segmentIds) => void ask(chapterId, segmentIds),
    async checkBook() {
      const chapters = book.chapters.filter((c) =>
        c.segments.some((s) => s.is_dialogue && !s.reviewed && !s.recheck_speaker_id),
      );
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

  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-20 border-b border-line bg-bg/85 backdrop-blur">
        <div className="mx-auto flex h-14 max-w-5xl items-center gap-6 px-6">
          <Link href="/" className="text-sm font-semibold tracking-tight">
            {book.name}
          </Link>
          <nav className="flex gap-1">
            {VIEWS.map((v) => (
              <button
                key={v}
                onClick={() => setView(v)}
                className={`rounded-md px-3 py-1.5 text-sm transition-colors ${
                  view === v ? "bg-ink/[0.06] font-medium" : "text-muted hover:text-ink"
                }`}
              >
                {TAB_LABELS[v]}
              </button>
            ))}
          </nav>
          <div className="ml-auto text-xs">
            {ready.ready ? (
              <span className="flex items-center gap-1.5 text-emerald-700 dark:text-emerald-400">
                <span className="size-1.5 rounded-full bg-current" /> Ready to narrate
              </span>
            ) : ready.reviewed > 0 ? (
              <span className="text-muted">
                {ready.reviewed} checked · {ready.corrected} fixed
              </span>
            ) : null}
          </div>
        </div>
      </header>

      {error && (
        <div className="mx-auto mt-4 max-w-5xl px-6">
          <p className="rounded-md bg-red-500/10 px-4 py-2 text-sm text-red-600 dark:text-red-400">{error}</p>
        </div>
      )}

      {view === "Overview" && <Overview book={book} ready={ready} claude={claude} onOpen={setView} />}
      {view === "Fix" && loaded && (
        <FixView
          book={book}
          edits={edits}
          claude={claude}
          batch={fixBatch}
          onBatch={setFixBatch}
          onDone={() => setView("Overview")}
          onOpenInChapter={(chapter, segment) => {
            setReadAt({ chapter, segment });
            setView("Read");
          }}
        />
      )}
      {view === "Cast" && <CastView book={book} edits={edits} />}
      {view === "Read" && <ReadView book={book} edits={edits} at={readAt} onNavigate={setReadAt} />}
    </div>
  );
}
