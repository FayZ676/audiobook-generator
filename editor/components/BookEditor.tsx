"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { changeSegment, saveCharacter } from "@/app/actions";
import type { Book, CastMember, SegmentChange } from "@/lib/model";
import { nextId } from "@/lib/model";
import CastView from "./CastView";
import ReadView from "./ReadView";
import ReviewView from "./ReviewView";

export type Edits = {
  changeSegment(chapterId: string, segmentId: string, change: SegmentChange): void;
  saveCharacter(member: CastMember): void;
  /** Adds a character by name, with voice traits to fix in the cast later. */
  addCharacter(name: string): CastMember;
};

const VIEWS = ["Review", "Cast", "Read"] as const;
type View = (typeof VIEWS)[number];

/** Holds the book in memory and saves every edit to disk as it's made. */
export default function BookEditor({ initial, initialView }: { initial: Book; initialView?: string }) {
  const [book, setBook] = useState(initial);
  const [view, setViewState] = useState<View>(
    VIEWS.find((v) => v.toLowerCase() === initialView) ?? "Review",
  );
  const setView = (v: View) => {
    setViewState(v);
    window.history.replaceState(null, "", `?view=${v.toLowerCase()}`); // a reload keeps the view
  };
  const [readAt, setReadAt] = useState<{ chapter: string; segment?: string }>({
    chapter: initial.chapters[0]?.id ?? "",
  });
  const [error, setError] = useState<string | null>(null);

  const save = (write: Promise<void>) =>
    write.catch((e: Error) => setError(`Couldn't save: ${e.message}. Reload to see what's on disk.`));

  const edits: Edits = {
    changeSegment(chapterId, segmentId, change) {
      setBook((b) => ({
        ...b,
        chapters: b.chapters.map((c) =>
          c.id !== chapterId
            ? c
            : { ...c, segments: c.segments.map((s) => (s.id === segmentId ? { ...s, ...change } : s)) },
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

  const progress = useMemo(() => {
    const lines = book.chapters.flatMap((c) => c.segments.filter((s) => s.is_dialogue));
    return { reviewed: lines.filter((s) => s.reviewed).length, total: lines.length };
  }, [book]);

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
                {v}
              </button>
            ))}
          </nav>
          <div className="ml-auto flex items-center gap-3 text-xs text-muted">
            <span className="tabular-nums">
              {progress.reviewed.toLocaleString()} / {progress.total.toLocaleString()} lines reviewed
            </span>
            <div className="h-1 w-24 overflow-hidden rounded-full bg-line">
              <div
                className="h-full rounded-full bg-accent transition-[width] duration-500"
                style={{ width: `${(100 * progress.reviewed) / Math.max(1, progress.total)}%` }}
              />
            </div>
          </div>
        </div>
      </header>

      {error && (
        <div className="mx-auto mt-4 max-w-5xl px-6">
          <p className="rounded-md bg-red-500/10 px-4 py-2 text-sm text-red-600 dark:text-red-400">{error}</p>
        </div>
      )}

      {view === "Review" && (
        <ReviewView
          book={book}
          edits={edits}
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
