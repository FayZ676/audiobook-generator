"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import type { Book, Segment, SegmentChange } from "@/lib/model";
import { displayName, likelySpeakers } from "@/lib/model";
import type { Edits } from "./BookEditor";
import Prose, { SpeakerDot } from "./Prose";
import SpeakerPicker from "./SpeakerPicker";

type Item = { chapter: string; index: number; segment: Segment };
type Undo = { chapter: string; segment: string; before: SegmentChange };

/** Every unreviewed line of dialogue, least confident first. Confirming or
 * correcting a line takes it off the list; work up until the lines look right. */
export default function ReviewView({
  book,
  edits,
  onOpenInChapter,
}: {
  book: Book;
  edits: Edits;
  onOpenInChapter: (chapter: string, segment: string) => void;
}) {
  const unreviewed = useMemo<Item[]>(
    () =>
      book.chapters
        .flatMap((c) =>
          c.segments.map((segment, index) => ({ chapter: c.id, index, segment })).filter((i) => i.segment.is_dialogue),
        )
        .filter((i) => !i.segment.reviewed)
        .sort((a, b) => confidence(a) - confidence(b)),
    [book],
  );
  const [below, setBelow] = useState(DEFAULT_BELOW);
  const queue = useMemo(() => unreviewed.filter((i) => confidence(i) < below), [unreviewed, below]);
  const [focusId, setFocusId] = useState<string | null>(null);
  const [undos, setUndos] = useState<Undo[]>([]);
  const searchRef = useRef<HTMLInputElement>(null);
  const focusedRef = useRef<HTMLDivElement>(null);

  const at = Math.max(0, queue.findIndex((i) => key(i) === focusId));
  const focused = queue[at];
  const chapter = focused && book.chapters.find((c) => c.id === focused.chapter)!;
  const likely = focused ? likelySpeakers(chapter, focused.index, book.cast) : [];

  const decide = (item: Item, speaker: string) => {
    const s = item.segment;
    setUndos((u) => [...u.slice(-50), { chapter: item.chapter, segment: s.id, before: { speaker_id: s.speaker_id, reviewed: s.reviewed } }]);
    edits.changeSegment(item.chapter, s.id, { speaker_id: speaker, reviewed: true });
    const next = queue[at + 1] ?? queue[at - 1];
    setFocusId(next ? key(next) : null);
  };

  const undo = () => {
    const last = undos.at(-1);
    if (!last) return;
    setUndos((u) => u.slice(0, -1));
    edits.changeSegment(last.chapter, last.segment, last.before);
    setFocusId(`${last.chapter}/${last.segment}`);
  };

  const move = (by: number) => {
    const next = queue[Math.min(queue.length - 1, Math.max(0, at + by))];
    if (next) setFocusId(key(next));
  };

  // Latest handlers for the key listener, without re-adding it every render.
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
  }, [focusId]);

  const header = (
    <div className="sticky top-14 z-10 -mx-6 mb-4 flex items-center justify-between gap-3 bg-bg/90 px-6 py-3 text-xs text-muted backdrop-blur">
      <Thresholds
        unreviewed={unreviewed}
        below={below}
        onChange={(t) => {
          setBelow(t);
          setFocusId(null);
          window.scrollTo({ top: 0, behavior: "smooth" });
        }}
      />
      <span className="whitespace-nowrap text-sm text-ink">
        <span className="font-semibold tabular-nums">{queue.length.toLocaleString()}</span>{" "}
        <span className="text-muted">{queue.length === 1 ? "line" : "lines"} left</span>
      </span>
    </div>
  );

  const higher = THRESHOLDS.find((t) => t > below && unreviewed.some((i) => confidence(i) < t));

  if (!focused) {
    return (
      <main className="mx-auto max-w-3xl px-6 pb-32 pt-4">
        {header}
        <div className="py-20 text-center">
          <p className="text-2xl font-semibold tracking-tight">
            {unreviewed.length === 0 ? "Every line is reviewed." : `Every line below ${label(below)} is reviewed.`}
          </p>
          <p className="mt-2 text-sm text-muted">
            {higher !== undefined ? (
              <button onClick={() => setBelow(higher)} className="text-accent hover:underline">
                Keep going with lines below {label(higher)}
              </button>
            ) : undos.length > 0 ? (
              "Press Z to undo the last one."
            ) : (
              "Use Read to look through any chapter."
            )}
          </p>
        </div>
      </main>
    );
  }

  const p = focused.segment.paragraph;
  const context = chapter.segments.filter((s) => s.paragraph >= p - 2 && s.paragraph <= p + 1);
  const rest = queue.slice(at + 1, at + 40);

  return (
    <main className="mx-auto max-w-3xl px-6 pb-32 pt-4">
      {header}

      {queue.slice(Math.max(0, at - 2), at).map((item) => (
        <Row key={key(item)} item={item} book={book} onClick={() => setFocusId(key(item))} />
      ))}

      <div ref={focusedRef} className="my-3 scroll-mt-32 rounded-xl border border-line bg-panel p-6 shadow-[0_1px_2px_rgba(0,0,0,0.04),0_8px_24px_-12px_rgba(0,0,0,0.12)]">
        <div className="mb-5 flex items-center gap-3 text-xs text-muted">
          <Confidence value={focused.segment.confidence} />
          <button onClick={() => onOpenInChapter(focused.chapter, focused.segment.id)} className="truncate hover:text-ink">
            {chapter.title}
          </button>
        </div>
        <Prose segments={context} cast={book.cast} highlight={focused.segment.id} dim />
        <div className="mt-6 flex flex-wrap items-center gap-3 border-t border-line pt-5">
          <button
            onClick={() => decide(focused, focused.segment.speaker_id)}
            className="rounded-full bg-accent px-4 py-1.5 text-[13px] font-medium text-white transition-opacity hover:opacity-90"
          >
            {displayName(book.cast, focused.segment.speaker_id)} is right ↵
          </button>
          <span className="text-xs text-muted">or</span>
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
          <Hint k="↵">correct</Hint>
          <Hint k="1–9">pick</Hint>
          <Hint k="/">search</Hint>
          <Hint k="↑↓">move</Hint>
          <Hint k="Z">undo</Hint>
          <Hint k="O">open in chapter</Hint>
        </div>
      </div>

      {rest.map((item) => (
        <Row key={key(item)} item={item} book={book} onClick={() => setFocusId(key(item))} />
      ))}
      {queue.length > at + 41 ? (
        <p className="py-4 text-center text-xs text-muted">and {(queue.length - at - 41).toLocaleString()} more</p>
      ) : (
        <div className="mt-6 flex items-center gap-4 text-xs text-muted">
          <span className="h-px flex-1 bg-line" />
          <span>
            End of lines below {label(below)}
            {higher !== undefined && (
              <>
                {" · "}
                <button onClick={() => setBelow(higher)} className="text-accent hover:underline">
                  keep going below {label(higher)}
                </button>
              </>
            )}
          </span>
          <span className="h-px flex-1 bg-line" />
        </div>
      )}
    </main>
  );
}

// Review stops at lines this confident unless a person asks for more.
const THRESHOLDS = [0.5, 0.7, 0.8, 0.9, Infinity];
const DEFAULT_BELOW = 0.8;

function confidence(item: Item) {
  return item.segment.confidence ?? -1; // unknown confidence comes first
}

function label(below: number) {
  return below === Infinity ? "any confidence" : below.toFixed(1);
}

/** Choose how far up to review: only lines less confident than this. */
function Thresholds({
  unreviewed,
  below,
  onChange,
}: {
  unreviewed: Item[];
  below: number;
  onChange: (below: number) => void;
}) {
  return (
    <div className="flex items-center gap-2">
      <span className="whitespace-nowrap">Review lines below</span>
      <div className="flex rounded-lg bg-ink/[0.05] p-0.5">
        {THRESHOLDS.map((t) => (
          <button
            key={t}
            onClick={() => onChange(t)}
            className={`rounded-md px-2.5 py-1 transition-colors ${
              t === below ? "bg-panel font-medium text-ink shadow-sm" : "hover:text-ink"
            }`}
          >
            {t === Infinity ? "All" : t.toFixed(1)}
            <span className="ml-1.5 font-mono tabular-nums opacity-60">
              {unreviewed.filter((i) => confidence(i) < t).length}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}

function key(item: Item) {
  return `${item.chapter}/${item.segment.id}`;
}

function Row({ item, book, onClick }: { item: Item; book: Book; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left text-sm transition-colors hover:bg-ink/[0.03]"
    >
      <Confidence value={item.segment.confidence} />
      <span className="flex w-36 shrink-0 items-center gap-2 truncate text-muted">
        <SpeakerDot id={item.segment.speaker_id} />
        <span className="truncate">{displayName(book.cast, item.segment.speaker_id)}</span>
      </span>
      <span className="truncate font-serif">“{item.segment.text}”</span>
    </button>
  );
}

function Confidence({ value }: { value: number | null }) {
  const tone =
    value === null || value < 0.5
      ? "bg-red-500/12 text-red-700 dark:text-red-300"
      : value < 0.8
        ? "bg-amber-500/15 text-amber-800 dark:text-amber-300"
        : "bg-ink/[0.05] text-muted";
  return (
    <span className={`w-11 shrink-0 rounded-md py-0.5 text-center font-mono text-[11px] tabular-nums ${tone}`}>
      {value === null ? "—" : value.toFixed(2)}
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
