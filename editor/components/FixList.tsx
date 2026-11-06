"use client";

import { useEffect, useState } from "react";
import type { Book, LineRef, Readiness } from "@/lib/model";
import { READY_AFTER, displayName, lineKey, opinion, recheckCost } from "@/lib/model";
import type { Claude } from "./BookEditor";
import { SpeakerDot } from "./Prose";
import SidePanel, { SideRow } from "./SidePanel";

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
  open: boolean;
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
    <SidePanel
      side="left"
      open={open}
      head={
        focusSpeaker ? (
          <>
            <SpeakerDot id={focusSpeaker} />
            <span className="flex-1 truncate">{displayName(book.cast, focusSpeaker)}&apos;s lines</span>
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
        )
      }
    >
      {rows.slice(0, shown).map((l) => {
        const key = lineKey(l.chapter, l.segment.id);
        const s = l.segment;
        return (
          <SideRow key={key} id={`fix-${key}`} chosen={key === selectedKey} onClick={() => onPick(l)}>
            <SpeakerDot id={s.speaker_id} />
            <span className="min-w-0 flex-1 truncate font-serif text-[13px] text-ink/80">{s.text}</span>
            {opinion(s) === "disagrees" && <span className="text-[11px] text-accent">✦</span>}
          </SideRow>
        );
      })}
      {rows.length > shown && (
        <button onClick={() => setLimit(shown + PAGE)} className="px-5 py-2 text-xs text-muted hover:text-ink">
          More
        </button>
      )}
    </SidePanel>
  );
}
