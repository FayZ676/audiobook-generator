"use client";

import { useEffect, useState } from "react";
import type { Book, LineRef, Readiness, Sort } from "@/lib/model";
import { READY_AFTER, THRESHOLDS, displayName, lineKey, opinion, percent, recheckCost } from "@/lib/model";
import type { Claude } from "./BookEditor";
import { SpeakerDot } from "./Prose";
import SidePanel, { SideRow } from "./SidePanel";

const PAGE = 60;

/** The lines to look at, as the person chose them: under a confidence they
 * pick, least sure first or in the book's order, each row showing how sure
 * the model was. N walks the same list. Choosing a character in the cast
 * lists just their lines. */
export default function FixList({
  book,
  lines,
  selected,
  ready,
  under,
  sort,
  onChooseList,
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
  under: number;
  sort: Sort;
  onChooseList: (choice: { under?: number; sort?: Sort }) => void;
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
  useEffect(() => setLimit(PAGE), [focusSpeaker, under, sort]);

  useEffect(() => {
    if (selectedKey) document.getElementById(`fix-${selectedKey}`)?.scrollIntoView({ block: "nearest", behavior: "instant" });
  }, [selectedKey]);

  const left = lines.filter((l) => !l.segment.reviewed).length;
  const progress = claude.bookProgress;
  const cost = recheckCost(book.chapters);
  const control = "cursor-pointer appearance-none bg-transparent outline-none hover:text-ink";

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
        ) : (
          <>
            <span
              className={`tabular-nums ${ready.ready ? "text-emerald-700" : ""}`}
              title={
                ready.ready
                  ? "Ready to narrate"
                  : ready.reviewed
                    ? `${ready.corrected} fixed · ${ready.confirmedInARow} of ${READY_AFTER} right in a row needed to call it ready`
                    : undefined
              }
            >
              {left.toLocaleString()}
            </span>
            <span>·</span>
            <select
              value={under}
              onChange={(e) => onChooseList({ under: Number(e.target.value) })}
              className={control}
              title="Show lines the model was less sure of than this, and any Claude disagrees with"
            >
              {THRESHOLDS.map((t) => (
                <option key={t} value={t}>
                  {t === 1 ? "any confidence" : `under ${t * 100}%`}
                </option>
              ))}
            </select>
            <span>·</span>
            <button
              onClick={() => onChooseList({ sort: sort === "least-sure" ? "book" : "least-sure" })}
              className={`${control} flex-1 text-left`}
              title="Change the order"
            >
              {sort === "least-sure" ? "least sure first" : "book order"} ⇅
            </button>
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
            {opinion(s) === "disagrees" && (
              <span className="text-[11px] text-accent" title="Claude disagrees">
                ✦
              </span>
            )}
            <span className="w-8 text-right text-[11px] tabular-nums text-muted" title="How sure the model was">
              {percent(s)}%
            </span>
          </SideRow>
        );
      })}
      {rows.length === 0 && (
        <p className="px-5 py-2 text-xs text-muted">{focusSpeaker ? "No lines." : "Nothing left under this confidence."}</p>
      )}
      {rows.length > shown && (
        <button onClick={() => setLimit(shown + PAGE)} className="px-5 py-2 text-xs text-muted hover:text-ink">
          More
        </button>
      )}
    </SidePanel>
  );
}
