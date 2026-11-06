"use client";

import type { RefObject } from "react";
import type { Book, LineRef } from "@/lib/model";
import { displayName, opinion } from "@/lib/model";
import SpeakerPicker from "./SpeakerPicker";

/** The selected line's editor, docked under the text: who says it, Claude
 * Opus's answer or a way to ask, and the keys for each. */
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
    <div className="mx-auto w-full max-w-3xl rounded-2xl border border-line bg-panel/95 p-5 shadow-[0_12px_40px_-12px_rgba(0,0,0,0.25)] backdrop-blur">
      <div className="flex items-start gap-3">
        <p className="min-w-0 flex-1 truncate font-serif text-[15px]">“{s.text}”</p>
        <button onClick={onClose} className="shrink-0 text-xs text-muted hover:text-ink">
          Close <kbd className="font-mono text-[10px]">Esc</kbd>
        </button>
      </div>

      <div className="mt-3 text-sm">
        {view === "disagrees" ? (
          <div className="flex items-center gap-3 rounded-lg bg-accent/10 px-3 py-2">
            <span className="text-accent">✦</span>
            <span className="flex-1">
              Claude Opus thinks <strong className="font-medium">{displayName(book.cast, s.recheck_speaker_id!)}</strong> says
              this.
            </span>
            <button onClick={onClaude} className="rounded-full bg-accent px-3 py-1 text-[13px] font-medium text-white hover:opacity-90">
              Use that <kbd className="ml-1 font-mono text-[10px] opacity-70">A</kbd>
            </button>
          </div>
        ) : view === "agrees" ? (
          <p className="px-1 text-muted">✦ Claude Opus agrees.</p>
        ) : asking ? (
          <p className="flex items-center gap-2 px-1 text-muted">
            <span className="size-3 animate-spin rounded-full border-2 border-accent border-t-transparent" />
            Claude Opus is reading the chapter…
          </p>
        ) : (
          <button onClick={onClaude} className="flex items-center gap-2 px-1 text-muted hover:text-ink">
            <span className="text-accent">✦</span> Not sure? Ask Claude Opus
            <kbd className="rounded border border-line px-1 font-mono text-[10px]">A</kbd>
          </button>
        )}
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-2">
        <span className="mr-1 text-sm">Who says this?</span>
        <SpeakerPicker ref={searchRef} likely={likely} current={s.speaker_id} cast={book.cast} onPick={onPick} onAdd={onAdd} />
      </div>
      <div className="mt-3 flex flex-wrap gap-3 text-[11px] text-muted">
        <Hint k="↵">it&apos;s right</Hint>
        <Hint k="1–9">pick</Hint>
        <Hint k="/">search</Hint>
        <Hint k="N">next likely mistake</Hint>
        <Hint k="Z">undo</Hint>
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
