"use client";

import { useEffect, useState } from "react";
import type { Book, Segment } from "@/lib/model";
import { likelySpeakers } from "@/lib/model";
import type { Edits } from "./BookEditor";
import Prose from "./Prose";
import SpeakerPicker from "./SpeakerPicker";

/** A chapter as a script: click any line of dialogue to change its speaker. */
export default function ReadView({
  book,
  edits,
  at,
  onNavigate,
}: {
  book: Book;
  edits: Edits;
  at: { chapter: string; segment?: string };
  onNavigate: (at: { chapter: string; segment?: string }) => void;
}) {
  const chapter = book.chapters.find((c) => c.id === at.chapter) ?? book.chapters[0];
  const [picking, setPicking] = useState<Segment | null>(null);
  const index = picking ? chapter.segments.findIndex((s) => s.id === picking.id) : -1;
  const current = index >= 0 ? chapter.segments[index] : null;

  useEffect(() => {
    if (at.segment) document.getElementById(`line-${at.segment}`)?.scrollIntoView({ block: "center" });
    else window.scrollTo({ top: 0 });
  }, [at.chapter, at.segment]);

  useEffect(() => {
    const close = (e: KeyboardEvent) => e.key === "Escape" && setPicking(null);
    window.addEventListener("keydown", close);
    return () => window.removeEventListener("keydown", close);
  }, []);

  return (
    <div className="mx-auto flex max-w-5xl gap-10 px-6 pt-10">
      <nav className="sticky top-24 hidden h-[calc(100vh-8rem)] w-52 shrink-0 overflow-y-auto md:block">
        {book.chapters.map((c) => {
          const lines = c.segments.filter((s) => s.is_dialogue);
          const done = lines.filter((s) => s.reviewed).length;
          return (
            <button
              key={c.id}
              onClick={() => onNavigate({ chapter: c.id })}
              className={`block w-full rounded-md px-3 py-2 text-left text-[13px] transition-colors ${
                c.id === chapter.id ? "bg-ink/[0.06] font-medium" : "text-muted hover:text-ink"
              }`}
            >
              <span className="line-clamp-2">{c.title}</span>
              <span className="mt-0.5 block font-mono text-[10px] text-muted tabular-nums">
                {done}/{lines.length} reviewed
              </span>
            </button>
          );
        })}
      </nav>

      <main className="min-w-0 flex-1 pb-48">
        <Prose
          segments={chapter.segments}
          cast={book.cast}
          highlight={current?.id ?? at.segment}
          onPick={(s) => setPicking(s)}
        />
      </main>

      {current && (
        <div className="fixed inset-x-0 bottom-0 z-30 border-t border-line bg-panel/95 backdrop-blur">
          <div className="mx-auto flex max-w-5xl flex-wrap items-center gap-3 px-6 py-4">
            <span className="w-full truncate font-serif text-sm text-muted">“{current.text}”</span>
            <SpeakerPicker
              likely={likelySpeakers(chapter, index, book.cast)}
              current={current.speaker_id}
              cast={book.cast}
              onPick={(id) => {
                edits.changeSegment(chapter.id, current.id, { speaker_id: id, reviewed: true });
                setPicking(null);
              }}
              onAdd={(name) => {
                edits.changeSegment(chapter.id, current.id, { speaker_id: edits.addCharacter(name).id, reviewed: true });
                setPicking(null);
              }}
            />
            <button onClick={() => setPicking(null)} className="ml-auto text-xs text-muted hover:text-ink">
              Close · Esc
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
