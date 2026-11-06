"use client";

import { useEffect, useMemo, useState } from "react";
import type { Book, LineRef, Readiness } from "@/lib/model";
import { READY_AFTER, displayName, lineKey, mark, opinion, recheckCost } from "@/lib/model";
import type { Claude } from "./BookEditor";
import { SpeakerDot } from "./Prose";

const PAGE = 60;

/** The lines worth fixing, in the order N walks them, beside the book. Its
 * top says how far along the book is, and is where Claude is asked to check
 * it. Choosing a character in the cast lists just their lines. */
export default function FixList({
  book,
  lines,
  selected,
  ready,
  claude,
  focusSpeaker,
  open,
  onPick,
  onClearFocus,
}: {
  book: Book;
  lines: LineRef[];
  selected: LineRef | null;
  ready: Readiness;
  claude: Claude;
  focusSpeaker: string | null;
  open: boolean; // shown as a drawer on screens too narrow for it to sit beside the book
  onPick: (line: LineRef) => void;
  onClearFocus: () => void;
}) {
  const numbers = useMemo(() => new Map(book.chapters.map((c, i) => [c.id, `ch. ${i + 1}`])), [book.chapters]);
  const selectedKey = selected && lineKey(selected.chapter, selected.segment.id);
  const at = selectedKey ? lines.findIndex((l) => lineKey(l.chapter, l.segment.id) === selectedKey) : -1;

  // A page at a time, always far enough to show the open line.
  const [limit, setLimit] = useState(PAGE);
  const shown = Math.max(limit, at + PAGE / 2);
  useEffect(() => setLimit(PAGE), [focusSpeaker]);

  useEffect(() => {
    if (selectedKey) document.getElementById(`fix-${selectedKey}`)?.scrollIntoView({ block: "nearest", behavior: "smooth" });
  }, [selectedKey]);

  const left = lines.filter((l) => !l.segment.reviewed).length;
  const progress = claude.bookProgress;
  const cost = recheckCost(book.chapters);

  return (
    <aside
      className={`fixed bottom-0 left-0 top-12 z-30 w-72 flex-col border-r border-line bg-bg xl:flex ${
        open ? "flex shadow-2xl" : "hidden"
      }`}
    >
      <div className="space-y-2 border-b border-line px-4 pb-4 pt-3 text-[13px]">
        {focusSpeaker ? (
          <div className="flex items-center gap-2 font-medium">
            <SpeakerDot id={focusSpeaker} />
            <span className="flex-1 truncate">{displayName(book.cast, focusSpeaker)}&apos;s lines</span>
            <button onClick={onClearFocus} className="text-muted hover:text-ink" title="Back to lines worth fixing (Esc)">
              ✕
            </button>
          </div>
        ) : ready.ready ? (
          <p className="flex items-center gap-2 font-medium text-emerald-700 dark:text-emerald-400">
            <span className="size-1.5 rounded-full bg-current" /> Ready to narrate
          </p>
        ) : (
          <div>
            <p className="font-display text-[19px] italic leading-tight">
              Worth a look <span className="font-sans text-xs not-italic text-muted">· {left} left</span>
            </p>
            {ready.reviewed > 0 && (
              <p className="text-xs text-muted" title={`${READY_AFTER} in a row means the rest are very likely right`}>
                {ready.corrected} fixed · {ready.confirmedInARow}/{READY_AFTER} right in a row
              </p>
            )}
          </div>
        )}

        {!focusSpeaker &&
          (progress ? (
            <p className="flex items-center gap-2 text-xs text-muted">
              <span className="size-3 animate-spin rounded-full border-2 border-accent border-t-transparent" />
              Claude is reading chapter {Math.min(progress.done + 1, progress.total)} of {progress.total}
            </p>
          ) : (
            ready.unchecked > 0 && (
              <button
                onClick={claude.checkBook}
                className="flex items-center gap-1.5 text-xs text-muted hover:text-ink"
                title="Claude Opus reads each chapter and points out lines it disagrees with"
              >
                <span className="text-accent">✦</span> Check with Claude
                <span>~${cost < 0.1 ? cost.toFixed(2) : cost.toFixed(1)}</span>
              </button>
            )
          ))}
      </div>

      <ol className="flex-1 overflow-y-auto py-1">
        {lines.slice(0, shown).map((l) => {
          const key = lineKey(l.chapter, l.segment.id);
          return (
            <Row
              key={key}
              id={`fix-${key}`}
              line={l}
              chapter={numbers.get(l.chapter) ?? l.chapter}
              book={book}
              selected={key === selectedKey}
              onPick={onPick}
            />
          );
        })}
        {lines.length > shown && (
          <li>
            <button onClick={() => setLimit(shown + PAGE)} className="w-full px-4 py-3 text-left text-xs text-muted hover:text-ink">
              Show more ({lines.length - shown})
            </button>
          </li>
        )}
      </ol>

      <p className="border-t border-line px-4 py-2 text-[11px] text-muted">
        <kbd className="mr-1 rounded border border-line px-1 font-mono text-[10px]">N</kbd>next
        <kbd className="ml-3 mr-1 rounded border border-line px-1 font-mono text-[10px]">Z</kbd>undo
      </p>
    </aside>
  );
}

function Row({
  id,
  line,
  chapter,
  book,
  selected,
  onPick,
}: {
  id: string;
  line: LineRef;
  chapter: string;
  book: Book;
  selected: boolean;
  onPick: (line: LineRef) => void;
}) {
  const s = line.segment;
  const kind = mark(s);
  const claudePick = opinion(s) === "disagrees" ? s.recheck_speaker_id! : null;
  return (
    <li id={id}>
      <button
        onClick={() => onPick(line)}
        className={`block w-full px-4 py-2 text-left transition-colors ${
          selected ? "bg-accent/10" : "hover:bg-ink/[0.04]"
        } ${s.reviewed && !selected ? "opacity-50" : ""}`}
      >
        <span className="flex items-center gap-1.5 text-xs">
          <span className={`w-3 shrink-0 text-center ${kind === "disagrees" ? "text-accent" : kind === "unsure" ? "text-[8px] text-amber-500" : "text-muted"}`}>
            {s.reviewed ? "✓" : kind === "disagrees" ? "✦" : kind === "unsure" ? "●" : ""}
          </span>
          <SpeakerDot id={s.speaker_id} />
          <span className="truncate font-medium">{displayName(book.cast, s.speaker_id)}</span>
          {claudePick && (
            <span className="truncate text-accent">→ {displayName(book.cast, claudePick)}?</span>
          )}
          <span className="ml-auto shrink-0 pl-2 text-[11px] text-muted">{chapter}</span>
        </span>
        <span className="mt-0.5 line-clamp-2 pl-[18px] font-serif text-[13px] leading-snug text-ink/80">“{s.text}”</span>
      </button>
    </li>
  );
}
