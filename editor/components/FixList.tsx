"use client";

import { useEffect, useState } from "react";
import type { Book, LineRef, Readiness } from "@/lib/model";
import { READY_AFTER, displayName, lineKey, opinion, recheckCost } from "@/lib/model";
import type { Claude } from "./BookEditor";
import { SpeakerDot } from "./Prose";

const PAGE = 60;

/** The lines still worth a look, in the order N walks them: each a speaker's
 * dot and the words, nothing more. Choosing a character in the cast lists
 * just their lines. */
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
  const selectedKey = selected && lineKey(selected.chapter, selected.segment.id);
  const isSelected = (l: LineRef) => lineKey(l.chapter, l.segment.id) === selectedKey;
  // Checked lines leave the list, though the open one stays until it's left.
  const rows = focusSpeaker ? lines : lines.filter((l) => !l.segment.reviewed || isSelected(l));
  const at = selectedKey ? rows.findIndex(isSelected) : -1;

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
    <aside className={`fixed bottom-0 left-0 top-12 z-30 w-72 flex-col bg-bg xl:flex ${open ? "flex shadow-2xl" : "hidden"}`}>
      <div className="flex h-10 shrink-0 items-center gap-2 px-5 text-xs text-muted">
        {focusSpeaker ? (
          <>
            <SpeakerDot id={focusSpeaker} />
            <span className="flex-1 truncate text-ink">{displayName(book.cast, focusSpeaker)}</span>
            <button onClick={onClearFocus} className="hover:text-ink" title="Show everyone (Esc)">
              ✕
            </button>
          </>
        ) : ready.ready ? (
          <span className="text-emerald-700">Ready to narrate</span>
        ) : (
          <>
            <span
              className="flex-1"
              title={
                ready.reviewed
                  ? `${ready.corrected} fixed · ${ready.confirmedInARow} of ${READY_AFTER} right in a row needed to call it ready`
                  : undefined
              }
            >
              {left.toLocaleString()} to check
            </span>
            {progress ? (
              <span
                className="size-3 animate-spin rounded-full border-2 border-accent border-t-transparent"
                title={`Claude is reading chapter ${Math.min(progress.done + 1, progress.total)} of ${progress.total}`}
              />
            ) : (
              ready.unchecked > 0 && (
                <button
                  onClick={claude.checkBook}
                  className="text-accent hover:opacity-70"
                  title={`Check with Claude (~$${cost < 0.1 ? cost.toFixed(2) : cost.toFixed(1)}): it reads each chapter and points out lines it disagrees with`}
                >
                  ✦
                </button>
              )
            )}
          </>
        )}
      </div>

      <ol className="flex-1 overflow-y-auto pb-6">
        {rows.slice(0, shown).map((l) => {
          const key = lineKey(l.chapter, l.segment.id);
          const s = l.segment;
          return (
            <li key={key} id={`fix-${key}`}>
              <button
                onClick={() => onPick(l)}
                className={`flex w-full items-center gap-2.5 px-5 py-1.5 text-left transition-colors ${
                  key === selectedKey ? "bg-accent/10" : "hover:bg-ink/[0.035]"
                }`}
              >
                <SpeakerDot id={s.speaker_id} />
                <span className="min-w-0 flex-1 truncate font-serif text-[13px] text-ink/75">{s.text}</span>
                {opinion(s) === "disagrees" && <span className="text-[11px] text-accent">✦</span>}
              </button>
            </li>
          );
        })}
        {rows.length > shown && (
          <li>
            <button onClick={() => setLimit(shown + PAGE)} className="px-5 py-2 text-xs text-muted hover:text-ink">
              More
            </button>
          </li>
        )}
      </ol>
    </aside>
  );
}
