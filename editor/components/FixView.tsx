"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import type { Book, Segment, SegmentChange } from "@/lib/model";
import { READY_AFTER, displayName, likelySpeakers, needsLook, opinion, readiness, wasCorrected } from "@/lib/model";
import type { Claude, Edits } from "./BookEditor";
import Prose, { SpeakerDot } from "./Prose";
import SpeakerPicker from "./SpeakerPicker";

type Item = { chapter: string; index: number; segment: Segment };
type Undo = { chapter: string; segment: string; before: SegmentChange };

// Lines shown around the one being checked.
const SHOW_BEFORE = 3;
const SHOW_AFTER = 30;

/** One list of the lines most likely to be wrong: those Claude Opus
 * disagreed with first, then those the model was least sure of. Checked
 * lines keep their place, marked; the list picks up at the first unchecked
 * one. Stop once lines stop needing fixes. */
export default function FixView({
  book,
  edits,
  claude,
  onDone,
  onOpenInChapter,
}: {
  book: Book;
  edits: Edits;
  claude: Claude;
  onDone: () => void;
  onOpenInChapter: (chapter: string, segment: string) => void;
}) {
  // The order depends only on what the models said, never on what a person
  // did, so checking a line never moves it.
  const lines = useMemo(() => {
    const all: Item[] = [];
    for (const c of book.chapters)
      c.segments.forEach((segment, index) => {
        if (segment.reviewed || needsLook(segment)) all.push({ chapter: c.id, index, segment });
      });
    return all.sort(
      (a, b) =>
        Number(claudeDisagreed(b.segment)) - Number(claudeDisagreed(a.segment)) ||
        (a.segment.confidence ?? -1) - (b.segment.confidence ?? -1),
    );
  }, [book]);
  const [focusKey, setFocusKey] = useState<string | null>(null);
  const [undos, setUndos] = useState<Undo[]>([]);
  const [showChecked, setShowChecked] = useState(false);
  const searchRef = useRef<HTMLInputElement>(null);
  const focusedRef = useRef<HTMLDivElement>(null);

  const focused = lines.find((i) => key(i.chapter, i.segment.id) === focusKey) ?? lines.find((i) => !i.segment.reviewed);
  const at = focused ? lines.indexOf(focused) : lines.length;
  const chapter = focused && book.chapters.find((c) => c.id === focused.chapter)!;
  const suggested = focused?.segment.recheck_speaker_id ?? null;
  const likely =
    focused && chapter
      ? [...new Set([...(suggested ? [suggested] : []), ...likelySpeakers(chapter, focused.index, book.cast)])]
      : [];
  const askingFocused = !!focused && claude.asking.has(key(focused.chapter, focused.segment.id));
  const ready = readiness(book);

  const decide = (item: Item, speaker: string) => {
    const s = item.segment;
    setUndos((u) => [...u.slice(-50), { chapter: item.chapter, segment: s.id, before: { speaker_id: s.speaker_id, reviewed: s.reviewed } }]);
    edits.changeSegment(item.chapter, s.id, { speaker_id: speaker, reviewed: true });
    // On to the next unchecked line after this one.
    const i = lines.indexOf(item);
    const next = [...lines.slice(i + 1), ...lines.slice(0, i)].find((l) => !l.segment.reviewed);
    setFocusKey(next ? key(next.chapter, next.segment.id) : null);
  };

  /** A: take Claude's answer if it has one, else ask for it. */
  const useClaude = (item: Item) => {
    if (item.segment.recheck_speaker_id) decide(item, item.segment.recheck_speaker_id);
    else if (!claude.asking.has(key(item.chapter, item.segment.id))) claude.askLines(item.chapter, [item.segment.id]);
  };

  const undo = () => {
    const last = undos.at(-1);
    if (!last) return;
    setUndos((u) => u.slice(0, -1));
    edits.changeSegment(last.chapter, last.segment, last.before);
    setFocusKey(key(last.chapter, last.segment));
  };

  const move = (by: number) => {
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

  useEffect(() => {
    focusedRef.current?.scrollIntoView({ block: "nearest", behavior: "smooth" });
  }, [focusKey]);

  const before = showChecked ? lines.slice(0, at) : lines.slice(Math.max(0, at - SHOW_BEFORE), at);
  const hidden = at - before.length;
  const after = lines.slice(at + 1, at + 1 + SHOW_AFTER);
  const more = lines.length - at - 1 - after.length;

  const header = (
    <div className="sticky top-14 z-10 -mx-6 mb-4 flex items-center justify-between gap-4 bg-bg/90 px-6 py-3 text-xs text-muted backdrop-blur">
      <span>Most likely mistakes first. Stop when they stop needing fixes.</span>
      {ready.reviewed > 0 && !ready.ready && (
        <span className="whitespace-nowrap tabular-nums">
          {ready.confirmedInARow} of {READY_AFTER} right in a row
        </span>
      )}
    </div>
  );

  const readyBanner = ready.ready && (
    <div className="mb-4 flex items-center justify-between gap-4 rounded-lg bg-emerald-500/10 px-4 py-3 text-sm text-emerald-800 dark:text-emerald-300">
      <span>
        {ready.unchecked === 0
          ? "Every line has been checked, by you or Claude Opus."
          : `${READY_AFTER} lines in a row needed no fix, so the rest are very likely right.`}
      </span>
      <button onClick={onDone} className="shrink-0 font-medium hover:underline">
        Finish
      </button>
    </div>
  );

  const checkedAbove = (
    <>
      {hidden > 0 && (
        <button onClick={() => setShowChecked(true)} className="mb-1 px-3 py-1 text-xs text-muted hover:text-ink">
          Show {hidden} more checked {hidden === 1 ? "line" : "lines"}
        </button>
      )}
      <Lines lines={before} book={book} onFocus={setFocusKey} />
    </>
  );

  if (!focused || !chapter) {
    return (
      <main className="mx-auto max-w-3xl px-6 pb-32 pt-4">
        {header}
        {readyBanner}
        {checkedAbove}
        <div className="mt-4 rounded-xl border border-line bg-panel px-6 py-10 text-center">
          <p className="text-2xl font-semibold tracking-tight">Every line in the list is checked.</p>
          <button onClick={onDone} className="mt-6 h-9 rounded-full bg-accent px-5 text-[13px] font-medium text-white hover:opacity-90">
            Done
          </button>
        </div>
      </main>
    );
  }

  const p = focused.segment.paragraph;
  const context = chapter.segments.filter((s) => s.paragraph >= p - 2 && s.paragraph <= p + 1);

  return (
    <main className="mx-auto max-w-3xl px-6 pb-32 pt-4">
      {header}
      {readyBanner}
      {checkedAbove}
      <div
        ref={focusedRef}
        className="my-3 scroll-mt-28 rounded-xl border border-line bg-panel p-6 shadow-[0_1px_2px_rgba(0,0,0,0.04),0_8px_24px_-12px_rgba(0,0,0,0.12)]"
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
      <Lines lines={after} book={book} onFocus={setFocusKey} />
      {more > 0 && <p className="py-4 text-center text-xs text-muted">and {more.toLocaleString()} more</p>}
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

/** Claude Opus disagreed with the models' first answer (not the person's). */
function claudeDisagreed(segment: Segment): boolean {
  const first = segment.model_speaker_id ?? segment.speaker_id;
  return !!segment.recheck_speaker_id && segment.recheck_speaker_id !== first;
}

function key(chapter: string, segment: string) {
  return `${chapter}/${segment}`;
}

/** Lines of the list, each showing what was decided about it. */
function Lines({
  lines,
  book,
  onFocus,
}: {
  lines: Item[];
  book: Book;
  onFocus: (key: string) => void;
}) {
  return (
    <div>
      {lines.map((item) => {
        const s = item.segment;
        return (
          <button
            key={key(item.chapter, s.id)}
            onClick={() => onFocus(key(item.chapter, s.id))}
            className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left text-sm transition-colors hover:bg-ink/[0.03]"
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
