"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import type { Book, Segment, SegmentChange } from "@/lib/model";
import { READY_AFTER, displayName, likelySpeakers, needsLook, opinion, readiness, wasCorrected } from "@/lib/model";
import type { Claude, Edits } from "./BookEditor";
import Prose, { SpeakerDot } from "./Prose";
import SpeakerPicker from "./SpeakerPicker";

const BATCH = 25;

type Item = { chapter: string; index: number; segment: Segment };
export type FixBatch = { keys: string[]; number: number }; // keys are "chapter/segment"
type Undo = { chapter: string; segment: string; before: SegmentChange };

/** The lines most likely wrong, a batch at a time: those Claude Opus
 * disagreed with first, then those the model was least sure of. After each
 * batch, how many needed fixing says whether another is worth doing. */
export default function FixView({
  book,
  edits,
  claude,
  batch: saved,
  onBatch,
  onDone,
  onOpenInChapter,
}: {
  book: Book;
  edits: Edits;
  claude: Claude;
  /** The batch in progress, kept by the caller so leaving the view keeps it. */
  batch: FixBatch | null;
  onBatch: (batch: FixBatch) => void;
  onDone: () => void;
  onOpenInChapter: (chapter: string, segment: string) => void;
}) {
  const items = useMemo(() => {
    const all = new Map<string, Item>();
    for (const c of book.chapters)
      c.segments.forEach((segment, index) => segment.is_dialogue && all.set(key(c.id, segment.id), { chapter: c.id, index, segment }));
    return all;
  }, [book]);
  const leastSure = () =>
    [...items.entries()]
      .filter(([, i]) => needsLook(i.segment))
      .sort(
        ([, a], [, b]) =>
          Number(opinion(b.segment) === "disagrees") - Number(opinion(a.segment) === "disagrees") ||
          (a.segment.confidence ?? -1) - (b.segment.confidence ?? -1),
      )
      .slice(0, BATCH)
      .map(([k]) => k);

  const [first] = useState<FixBatch>(() => ({ keys: leastSure(), number: 1 }));
  useEffect(() => {
    if (!saved) onBatch(first); // keep the first batch from the first visit
  }, [saved, first, onBatch]);
  const { keys: batch, number: batchNumber } = saved ?? first;
  const [focusKey, setFocusKey] = useState<string | null>(null);
  const [undos, setUndos] = useState<Undo[]>([]);
  const searchRef = useRef<HTMLInputElement>(null);
  const focusedRef = useRef<HTMLDivElement>(null);

  const lines = batch.flatMap((k) => items.get(k) ?? []); // a rebuilt chapter may drop lines
  const done = lines.filter((i) => i.segment.reviewed).length;
  const firstOpen = lines.find((i) => !i.segment.reviewed);
  const focused = (focusKey && items.get(focusKey)) || firstOpen;
  const chapter = focused && book.chapters.find((c) => c.id === focused.chapter)!;
  const suggested = focused?.segment.recheck_speaker_id ?? null;
  const likely =
    focused && chapter
      ? [...new Set([...(suggested ? [suggested] : []), ...likelySpeakers(chapter, focused.index, book.cast)])]
      : [];
  const askingFocused = !!focused && claude.asking.has(key(focused.chapter, focused.segment.id));

  /** A: take Claude's answer if it has one, else ask for it. */
  const useClaude = (item: Item) => {
    if (item.segment.recheck_speaker_id) decide(item, item.segment.recheck_speaker_id);
    else if (!claude.asking.has(key(item.chapter, item.segment.id))) claude.askLines(item.chapter, [item.segment.id]);
  };
  const ready = readiness(book);

  const decide = (item: Item, speaker: string) => {
    const s = item.segment;
    setUndos((u) => [...u.slice(-50), { chapter: item.chapter, segment: s.id, before: { speaker_id: s.speaker_id, reviewed: s.reviewed } }]);
    edits.changeSegment(item.chapter, s.id, { speaker_id: speaker, reviewed: true });
    // On to the next unchecked line in the batch, after this one.
    const at = lines.indexOf(item);
    const next = [...lines.slice(at + 1), ...lines.slice(0, at)].find((i) => !i.segment.reviewed);
    setFocusKey(next ? key(next.chapter, next.segment.id) : null);
  };

  const undo = () => {
    const last = undos.at(-1);
    if (!last) return;
    setUndos((u) => u.slice(0, -1));
    edits.changeSegment(last.chapter, last.segment, last.before);
    setFocusKey(key(last.chapter, last.segment));
  };

  const nextBatch = () => {
    onBatch({ keys: leastSure(), number: batchNumber + 1 });
    setFocusKey(null);
    window.scrollTo({ top: 0 });
  };

  const move = (by: number) => {
    const at = focused ? lines.indexOf(focused) : -1;
    const next = lines[Math.min(lines.length - 1, Math.max(0, at + by))];
    if (next) setFocusKey(key(next.chapter, next.segment.id));
  };

  const keys = useRef<(e: KeyboardEvent) => void>(() => {});
  keys.current = (e) => {
    if (e.metaKey || e.ctrlKey || e.altKey || (e.target as HTMLElement).closest("input, textarea, select")) return;
    if (e.key === "ArrowDown" || e.key === "j") move(1);
    else if (e.key === "ArrowUp" || e.key === "k") move(-1);
    else if (e.key === "z" || e.key === "u") undo();
    else if (!focused) return;
    else if (e.key === "Enter") decide(focused, focused.segment.speaker_id);
    else if (/^[1-9]$/.test(e.key) && likely[Number(e.key) - 1]) decide(focused, likely[Number(e.key) - 1]);
    else if (e.key === "/") searchRef.current?.focus();
    else if (e.key === "a") useClaude(focused);
    else if (e.key === "o") onOpenInChapter(focused.chapter, focused.segment.id);
    else return;
    e.preventDefault();
  };
  useEffect(() => {
    const listener = (e: KeyboardEvent) => keys.current(e);
    window.addEventListener("keydown", listener);
    return () => window.removeEventListener("keydown", listener);
  }, []);

  const batchDone = !focused;
  useEffect(() => {
    if (batchDone) window.scrollTo({ top: 0, behavior: "smooth" });
    else focusedRef.current?.scrollIntoView({ block: "nearest", behavior: "smooth" });
  }, [focusKey, batchDone]);

  const fixedInBatch = lines.filter((i) => wasCorrected(i.segment)).length;
  const header = (
    <div className="sticky top-14 z-10 -mx-6 mb-4 flex items-center gap-4 bg-bg/90 px-6 py-3 text-xs text-muted backdrop-blur">
      <span className="whitespace-nowrap">
        Batch {batchNumber} · <span className="tabular-nums">{done}</span> of {lines.length} checked
        {fixedInBatch > 0 && <> · {fixedInBatch} fixed</>}
      </span>
      <div className="h-1 flex-1 overflow-hidden rounded-full bg-line">
        <div
          className="h-full rounded-full bg-accent transition-[width] duration-300"
          style={{ width: `${(100 * done) / Math.max(1, lines.length)}%` }}
        />
      </div>
    </div>
  );

  if (!focused || !chapter) {
    return (
      <main className="mx-auto max-w-3xl px-6 pb-32 pt-4">
        {header}
        <Checkpoint
          checked={lines.length}
          fixed={fixedInBatch}
          ready={ready.ready}
          more={[...items.values()].some((i) => !i.segment.reviewed)}
          onMore={nextBatch}
          onDone={onDone}
        />
        <Lines lines={lines} book={book} onFocus={setFocusKey} />
      </main>
    );
  }

  const p = focused.segment.paragraph;
  const context = chapter.segments.filter((s) => s.paragraph >= p - 2 && s.paragraph <= p + 1);

  return (
    <main className="mx-auto max-w-3xl px-6 pb-32 pt-4">
      {header}
      {ready.ready && (
        <div className="mb-4 flex items-center justify-between gap-4 rounded-lg bg-emerald-500/10 px-4 py-3 text-sm text-emerald-800 dark:text-emerald-300">
          <span>
            {READY_AFTER} lines right in a row. The rest are very likely right too.
          </span>
          <button onClick={onDone} className="shrink-0 font-medium hover:underline">
            Finish
          </button>
        </div>
      )}
      <div
        ref={focusedRef}
        className="scroll-mt-28 rounded-xl border border-line bg-panel p-6 shadow-[0_1px_2px_rgba(0,0,0,0.04),0_8px_24px_-12px_rgba(0,0,0,0.12)]"
      >
        <button
          onClick={() => onOpenInChapter(focused.chapter, focused.segment.id)}
          className="mb-5 block truncate text-xs text-muted hover:text-ink"
        >
          {chapter.title}
        </button>
        <Prose segments={context} cast={book.cast} highlight={focused.segment.id} dim />
        <ClaudeNote
          item={focused}
          book={book}
          asking={askingFocused}
          onUse={() => useClaude(focused)}
        />
        <div className="mt-6 flex flex-wrap items-center gap-3 border-t border-line pt-5">
          <span className="text-sm">Who says this?</span>
          <SpeakerPicker
            ref={searchRef}
            likely={likely}
            current={focused.segment.speaker_id}
            cast={book.cast}
            onPick={(id) => decide(focused, id)}
            onAdd={(name) => decide(focused, edits.addCharacter(name).id)}
          />
        </div>
        <div className="mt-4 hidden gap-3 text-[11px] text-muted sm:flex">
          <Hint k="↵">it&apos;s right</Hint>
          <Hint k="1–9">pick</Hint>
          <Hint k="/">search</Hint>
          <Hint k="A">{suggested ? "use Claude's answer" : "ask Claude"}</Hint>
          <Hint k="↑↓">move</Hint>
          <Hint k="Z">undo</Hint>
          <Hint k="O">open in chapter</Hint>
        </div>
      </div>
      <Lines lines={lines} book={book} focused={focused} onFocus={setFocusKey} />
    </main>
  );
}

/** What Claude Opus said about the line, or a way to ask it. */
function ClaudeNote({ item, book, asking, onUse }: { item: Item; book: Book; asking: boolean; onUse: () => void }) {
  const s = item.segment;
  const view = opinion(s);
  const box = "mt-5 flex items-center gap-3 rounded-lg px-4 py-2.5 text-sm";
  if (view === "disagrees")
    return (
      <div className={`${box} bg-accent/10`}>
        <span className="text-accent">✦</span>
        <span className="flex-1">
          Claude Opus thinks <strong className="font-medium">{displayName(book.cast, s.recheck_speaker_id!)}</strong> says
          this.
        </span>
        <button onClick={onUse} className="rounded-full bg-accent px-3 py-1 text-[13px] font-medium text-white hover:opacity-90">
          Use that <kbd className="ml-1 font-mono text-[10px] opacity-70">A</kbd>
        </button>
      </div>
    );
  if (view === "agrees")
    return (
      <div className={`${box} bg-ink/[0.04] text-muted`}>
        <span>✦</span> Claude Opus agrees.
      </div>
    );
  return (
    <div className={`${box} text-muted`}>
      {asking ? (
        <>
          <span className="size-3 animate-spin rounded-full border-2 border-accent border-t-transparent" />
          Claude Opus is reading the chapter…
        </>
      ) : (
        <button onClick={onUse} className="flex items-center gap-2 hover:text-ink">
          <span className="text-accent">✦</span> Not sure? Ask Claude Opus
          <kbd className="rounded border border-line px-1 font-mono text-[10px]">A</kbd>
        </button>
      )}
    </div>
  );
}

function key(chapter: string, segment: string) {
  return `${chapter}/${segment}`;
}

/** The end of a batch: whether another one is worth doing. */
function Checkpoint({
  checked,
  fixed,
  ready,
  more,
  onMore,
  onDone,
}: {
  checked: number;
  fixed: number;
  ready: boolean;
  more: boolean;
  onMore: () => void;
  onDone: () => void;
}) {
  const worthMore = more && !ready;
  return (
    <div className="rounded-xl border border-line bg-panel px-6 py-10 text-center">
      <p className="text-2xl font-semibold tracking-tight">
        {!more ? "Every line is checked." : ready ? "The rest look right." : `You fixed ${fixed} of ${checked}.`}
      </p>
      <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-muted">
        {!more
          ? "Nothing left to check."
          : ready
            ? `You confirmed the last ${READY_AFTER} lines without changing any, and the lines left are ones the model was surer of.`
            : "Still finding mistakes, so the next batch is worth a look."}
      </p>
      <div className="mt-6 flex justify-center gap-2">
        <button
          onClick={worthMore ? onMore : onDone}
          className="h-9 rounded-full bg-accent px-5 text-[13px] font-medium text-white hover:opacity-90"
        >
          {worthMore ? `Next ${BATCH} lines` : "Done"}
        </button>
        {more && (
          <button onClick={worthMore ? onDone : onMore} className="h-9 rounded-full border border-line px-5 text-[13px]">
            {worthMore ? "Stop here" : "Check more anyway"}
          </button>
        )}
      </div>
    </div>
  );
}

/** The batch, each line showing what was decided about it. */
function Lines({
  lines,
  book,
  focused,
  onFocus,
}: {
  lines: Item[];
  book: Book;
  focused?: Item;
  onFocus: (key: string) => void;
}) {
  return (
    <div className="mt-6">
      {lines.map((item) => {
        const s = item.segment;
        const isFocused = item === focused;
        return (
          <button
            key={key(item.chapter, s.id)}
            onClick={() => onFocus(key(item.chapter, s.id))}
            className={`flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left text-sm transition-colors hover:bg-ink/[0.03] ${
              isFocused ? "bg-ink/[0.04]" : ""
            }`}
          >
            <Status segment={s} />
            <span className={`flex w-40 shrink-0 items-center gap-2 truncate ${s.reviewed ? "" : "text-muted"}`}>
              <SpeakerDot id={s.speaker_id} />
              <span className="truncate">{displayName(book.cast, s.speaker_id)}</span>
            </span>
            <span className={`min-w-0 flex-1 truncate font-serif ${s.reviewed ? "text-muted" : ""}`}>“{s.text}”</span>
            {!s.reviewed && opinion(s) === "disagrees" && (
              <span className="shrink-0 rounded-full bg-accent/10 px-2 py-0.5 text-[11px] text-accent">
                Claude: {displayName(book.cast, s.recheck_speaker_id!)}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}

function Status({ segment }: { segment: Segment }) {
  if (!segment.reviewed) return <span className="size-4 shrink-0 rounded-full border border-line" />;
  if (wasCorrected(segment))
    return (
      <span className="flex size-4 shrink-0 items-center justify-center rounded-full bg-amber-500 text-[10px] text-white" title="Fixed">
        ✎
      </span>
    );
  return (
    <span className="flex size-4 shrink-0 items-center justify-center rounded-full bg-emerald-600 text-[10px] text-white" title="Right">
      ✓
    </span>
  );
}

function Hint({ k, children }: { k: string; children: React.ReactNode }) {
  return (
    <span>
      <kbd className="mr-1 rounded border border-line px-1 font-mono text-[10px]">{k}</kbd>
      {children}
    </span>
  );
}
