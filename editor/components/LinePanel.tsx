"use client";

import type { RefObject } from "react";
import type { Book, LineRef } from "@/lib/model";
import { displayName, opinion } from "@/lib/model";
import SpeakerPicker from "./SpeakerPicker";

/** One thing: who says the open line. The line itself is outlined in the
 * book above. Claude Opus speaks up only when it thinks someone else does. */
export default function LinePanel({
  book,
  line,
  likely,
  asking,
  searchRef,
  onPick,
  onAdd,
  onClaude,
  onClose,
}: {
  book: Book;
  line: LineRef;
  likely: string[];
  asking: boolean;
  searchRef: RefObject<HTMLInputElement | null>;
  onPick: (speakerId: string) => void;
  onAdd: (name: string) => void;
  onClaude: () => void;
  onClose: () => void;
}) {
  const s = line.segment;
  const view = opinion(s);
  return (
    <div className="mx-auto w-full max-w-[44rem] rounded-2xl border border-line bg-panel px-5 py-4 shadow-[0_18px_50px_-24px_rgba(60,40,20,0.28)]">
      {view === "disagrees" && (
        <div className="mb-3 flex items-center gap-3 text-sm">
          <span className="text-accent">✦</span>
          <span className="flex-1">
            Claude thinks <strong className="font-medium">{displayName(book.cast, s.recheck_speaker_id!)}</strong> says this.
          </span>
          <button onClick={onClaude} className="rounded-full bg-accent px-3 py-1 text-[13px] font-medium text-white hover:opacity-90">
            Use that <kbd className="ml-1 font-mono text-[10px] opacity-70">A</kbd>
          </button>
        </div>
      )}

      <div className="flex items-start gap-3">
        <span className="mt-1 shrink-0 font-display text-[17px] italic text-muted">Who says this?</span>
        <div className="min-w-0 flex-1">
          <SpeakerPicker
            ref={searchRef}
            likely={likely}
            current={s.speaker_id}
            claudePick={s.recheck_speaker_id ?? null}
            cast={book.cast}
            onPick={onPick}
            onAdd={onAdd}
          />
        </div>
        <button onClick={onClose} className="mt-1 shrink-0 text-muted hover:text-ink" title="Close (Esc)">
          ✕
        </button>
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-4 text-[11px] text-muted">
        <Hint k="↵">it&apos;s right</Hint>
        <Hint k="1–9">pick</Hint>
        {asking ? (
          <span className="flex items-center gap-1.5">
            <span className="size-2.5 animate-spin rounded-full border-[1.5px] border-accent border-t-transparent" />
            Claude is reading the chapter…
          </span>
        ) : (
          view === null && (
            <button onClick={onClaude} className="hover:text-ink">
              <Hint k="A">ask Claude</Hint>
            </button>
          )
        )}
      </div>
    </div>
  );
}

export function Hint({ k, children }: { k: string; children: React.ReactNode }) {
  return (
    <span>
      <kbd className="mr-1 rounded border border-line px-1 font-mono text-[10px]">{k}</kbd>
      {children}
    </span>
  );
}
