"use client";

import Link from "next/link";
import { useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";
import { askClaude, changeSegment, saveCharacter } from "@/app/actions";
import type { Book, CastMember, LineRef, Segment, SegmentChange } from "@/lib/model";
import type { Sort } from "@/lib/model";
import { DEFAULT_UNDER, THRESHOLDS, applyChange, fixLines, likelySpeakers, lineKey, nextId, readiness, splitTitle } from "@/lib/model";
import CastPanel from "./CastPanel";
import FixList from "./FixList";
import LinePanel from "./LinePanel";
import Prose from "./Prose";
import { SideToggle } from "./SidePanel";

/** Asking Claude Opus about lines, which happens only when a person asks. */
export type Claude = {
  /** Lines being asked about now, as lineKey(chapter, segment). */
  asking: Set<string>;
  askLines(chapterId: string, segmentIds: string[]): void;
  /** Every unreviewed line of the book, a chapter per request. */
  checkBook(): void;
  bookProgress: { done: number; total: number } | null;
};

type Selection = {
  chapter: string;
  segment: string;
  // Reached with N, so deciding moves on to the next; clicked, so it closes.
  stepping: boolean;
};
type Undo = { chapter: string; segment: string; before: SegmentChange };

/** The book, with quiet controls to find lines and fix who says them. Every
 * edit is saved to disk as it's made. */
export default function BookEditor({ initial }: { initial: Book }) {
  const [book, setBook] = useState(initial);
  const [selection, setSelection] = useState<Selection | null>(null);
  const [focusSpeaker, setFocusSpeaker] = useState<string | null>(null);
  const [castOpen, setCastOpen] = useState(false);
  // The list of lines worth a look: open beside the book on wide screens, a
  // drawer over it on narrow ones, so closed there to begin with.
  const [listOpen, setListOpen] = useState(true);
  const narrow = () => window.innerWidth < 1280; // Tailwind's xl
  useEffect(() => {
    if (narrow()) setListOpen(false);
  }, []);
  const [undos, setUndos] = useState<Undo[]>([]);
  const [error, setError] = useState<string | null>(null);
  const searchRef = useRef<HTMLInputElement>(null);

  // One chapter at a time, kept in the URL so a reload comes back to it.
  const [reading, setReading] = useState(initial.chapters[0]?.id ?? "");
  // A line to scroll to once its chapter is showing.
  const pending = useRef<{ chapter: string; segment: string } | null>(null);
  // Read before the effect below writes the URL (layout effects run in order).
  useLayoutEffect(() => {
    const id = new URLSearchParams(window.location.search).get("chapter");
    if (id && initial.chapters.some((c) => c.id === id)) setReading(id);
  }, [initial.chapters]);
  useLayoutEffect(() => {
    const url = new URL(window.location.href);
    url.searchParams.set("chapter", reading);
    window.history.replaceState(null, "", url);
    const line = pending.current;
    pending.current = null;
    const el = line?.chapter === reading ? document.getElementById(`line-${line.chapter}-${line.segment}`) : null;
    if (el) jumpTo(el);
    else window.scrollTo(0, 0);
  }, [reading]);

  const report = (what: string) => (e: Error) => setError(`${what}: ${e.message}. Reload to see what's on disk.`);

  const changeLine = (chapterId: string, segmentId: string, change: SegmentChange) => {
    setBook((b) => ({
      ...b,
      chapters: b.chapters.map((c) =>
        c.id !== chapterId
          ? c
          : { ...c, segments: c.segments.map((s) => (s.id === segmentId ? applyChange(s, change, new Date().toISOString()) : s)) },
      ),
    }));
    changeSegment(book.name, chapterId, segmentId, change).catch(report("Couldn't save"));
  };

  const saveMember = (member: CastMember) => {
    setBook((b) => ({
      ...b,
      cast: b.cast.some((m) => m.id === member.id) ? b.cast.map((m) => (m.id === member.id ? member : m)) : [...b.cast, member],
    }));
    saveCharacter(book.name, member).catch(report("Couldn't save"));
  };

  // Claude Opus, only when asked.
  const [asking, setAsking] = useState<Set<string>>(new Set());
  const [bookProgress, setBookProgress] = useState<Claude["bookProgress"]>(null);
  const ask = async (chapterId: string, segmentIds: string[]) => {
    const keys = segmentIds.map((id) => lineKey(chapterId, id));
    setAsking((a) => new Set([...a, ...keys]));
    try {
      const answers = await askClaude(book.name, chapterId, segmentIds);
      setBook((b) => ({
        ...b,
        chapters: b.chapters.map((c) =>
          c.id !== chapterId
            ? c
            : { ...c, segments: c.segments.map((s) => (answers[s.id] ? { ...s, recheck_speaker_id: answers[s.id] } : s)) },
        ),
      }));
    } catch (e) {
      report("Couldn't ask Claude")(e as Error);
    } finally {
      setAsking((a) => new Set([...a].filter((k) => !keys.includes(k))));
    }
  };
  const claude: Claude = {
    asking,
    askLines: (chapterId, segmentIds) => void ask(chapterId, segmentIds),
    async checkBook() {
      const chapters = book.chapters.filter((c) => c.segments.some((s) => s.is_dialogue && !s.reviewed && !s.recheck_speaker_id));
      setBookProgress({ done: 0, total: chapters.length });
      for (const [i, c] of chapters.entries()) {
        await ask(c.id, []); // none named: every unreviewed line of the chapter
        setBookProgress({ done: i + 1, total: chapters.length });
      }
      setBookProgress(null);
    },
    bookProgress,
  };

  const ready = useMemo(() => readiness(book), [book]);
  // Which lines to look at, and in what order: the person's choice, kept in
  // this browser.
  const [under, setUnder] = useState<number>(DEFAULT_UNDER);
  const [sort, setSort] = useState<Sort>("least-sure");
  useEffect(() => {
    try {
      const saved = JSON.parse(localStorage.getItem("fix-list") ?? "{}");
      if (THRESHOLDS.includes(saved.under)) setUnder(saved.under);
      if (saved.sort === "book" || saved.sort === "least-sure") setSort(saved.sort);
    } catch {}
  }, []);
  const chooseList = (next: { under?: number; sort?: Sort }) => {
    const value = { under: next.under ?? under, sort: next.sort ?? sort };
    setUnder(value.under);
    setSort(value.sort);
    try {
      localStorage.setItem("fix-list", JSON.stringify(value));
    } catch {}
  };
  const order = useMemo(() => fixLines(book, under, sort), [book, under, sort]);
  const selected: LineRef | null = useMemo(() => {
    if (!selection) return null;
    const chapter = book.chapters.find((c) => c.id === selection.chapter);
    const index = chapter?.segments.findIndex((s) => s.id === selection.segment) ?? -1;
    return chapter && index >= 0 ? { chapter: chapter.id, index, segment: chapter.segments[index] } : null;
  }, [book, selection]);

  /** Straight to a line, no scrolling: showing its chapter first if need be. */
  const scrollTo = (chapter: string, segmentId: string) => {
    if (chapter !== reading) {
      pending.current = { chapter, segment: segmentId };
      setReading(chapter);
    } else
      requestAnimationFrame(() => {
        const el = document.getElementById(`line-${chapter}-${segmentId}`);
        if (el) jumpTo(el);
      });
  };
  const openChapter = (id: string) => {
    setSelection(null);
    setReading(id);
  };
  const at = book.chapters.findIndex((c) => c.id === reading);
  const chapter = book.chapters[at];
  const [prev, next] = [book.chapters[at - 1], book.chapters[at + 1]];

  const select = (line: { chapter: string; segment: Segment }, stepping: boolean) => {
    setSelection({ chapter: line.chapter, segment: line.segment.id, stepping });
    scrollTo(line.chapter, line.segment.id);
  };

  const linesOf = (speaker: string): LineRef[] =>
    book.chapters.flatMap((c) =>
      c.segments.flatMap((segment, index) =>
        segment.is_dialogue && segment.speaker_id === speaker ? [{ chapter: c.id, index, segment }] : [],
      ),
    );
  // What the left list shows, and what N steps through.
  const listed = focusSpeaker ? linesOf(focusSpeaker) : order;

  /** N: the next line most likely wrong, or, finding one character, their next line. */
  const step = (by: 1 | -1) => {
    const isSelected = (l: { chapter: string; segment: Segment }) =>
      !!selected && l.chapter === selected.chapter && l.segment.id === selected.segment.id;
    const candidates = focusSpeaker ? listed : order.filter((l) => !l.segment.reviewed || isSelected(l));
    if (!candidates.length) return;
    const at = candidates.findIndex(isSelected);
    select(candidates[(at + by + candidates.length) % candidates.length], true);
  };

  const decide = (speaker: string) => {
    if (!selected) return;
    const s = selected.segment;
    setUndos((u) => [...u.slice(-50), { chapter: selected.chapter, segment: s.id, before: { speaker_id: s.speaker_id, reviewed: s.reviewed } }]);
    changeLine(selected.chapter, s.id, { speaker_id: speaker, reviewed: true });
    if (selection?.stepping && !focusSpeaker) {
      // On to the next unchecked line most likely wrong, after this one.
      const at = order.findIndex((l) => l.chapter === selected.chapter && l.segment.id === s.id);
      const next = [...order.slice(at + 1), ...order.slice(0, Math.max(0, at))].find((l) => !l.segment.reviewed);
      if (next) select(next, true);
      else setSelection(null);
    } else setSelection(null);
  };

  const undo = () => {
    const last = undos.at(-1);
    if (!last) return;
    setUndos((u) => u.slice(0, -1));
    changeLine(last.chapter, last.segment, last.before);
    const segment = book.chapters.find((c) => c.id === last.chapter)?.segments.find((s) => s.id === last.segment);
    if (segment) select({ chapter: last.chapter, segment }, selection?.stepping ?? false);
  };

  const likely = useMemo(() => {
    if (!selected) return [];
    const chapter = book.chapters.find((c) => c.id === selected.chapter)!;
    const suggested = selected.segment.recheck_speaker_id;
    return [...new Set([...(suggested ? [suggested] : []), ...likelySpeakers(chapter, selected.index, book.cast)])];
  }, [book, selected]);

  /** A: take Claude's answer if it has one, else ask for it. */
  const useClaude = () => {
    if (!selected) return;
    const s = selected.segment;
    if (s.recheck_speaker_id) decide(s.recheck_speaker_id);
    else if (!asking.has(lineKey(selected.chapter, s.id))) claude.askLines(selected.chapter, [s.id]);
  };

  const addCharacter = (name: string) => {
    const member: CastMember = { id: nextId(book.cast), names: [name], age: "middle-aged", gender: "male", voice: null };
    saveMember(member);
    decide(member.id);
  };

  // On a narrow screen the bars cover the book, so only one is open at a time.
  const toggleList = () => {
    if (!listOpen && narrow()) setCastOpen(false);
    setListOpen(!listOpen);
  };
  const toggleCast = () => {
    if (!castOpen && narrow()) setListOpen(false);
    setCastOpen(!castOpen);
  };

  // Keys, with the latest handlers, without re-adding the listener every render.
  const keys = useRef<(e: KeyboardEvent) => void>(() => {});
  keys.current = (e) => {
    if (e.metaKey || e.ctrlKey || e.altKey || (e.target as HTMLElement).closest("input, textarea, select")) return;
    if (e.key === "Escape") {
      if (selection) setSelection(null);
      else if (narrow() && (castOpen || listOpen)) {
        setCastOpen(false);
        setListOpen(false);
      }
      else setFocusSpeaker(null);
    } else if (e.key === "n" || e.key === "j") step(1);
    else if (e.key === "N" || e.key === "p" || e.key === "k") step(-1);
    else if (e.key === "[") toggleList();
    else if (e.key === "]" || e.key === "c") toggleCast();
    else if (e.key === "z" || e.key === "u") undo();
    else if (!selected) return;
    else if (e.key === "Enter") decide(selected.segment.speaker_id);
    else if (/^[1-9]$/.test(e.key) && likely[Number(e.key) - 1]) decide(likely[Number(e.key) - 1]);
    else if (e.key === "/") searchRef.current?.focus();
    else if (e.key === "a") useClaude();
    else return;
    e.preventDefault();
  };
  useEffect(() => {
    const listener = (e: KeyboardEvent) => keys.current(e);
    window.addEventListener("keydown", listener);
    return () => window.removeEventListener("keydown", listener);
  }, []);

  // Stable per chapter, so a chapter that didn't change doesn't re-render.
  const pickIn = useCallback(
    (chapter: string) => (segment: Segment) => setSelection({ chapter, segment: segment.id, stepping: false }),
    [],
  );
  const pickers = useMemo(() => new Map(initial.chapters.map((c) => [c.id, pickIn(c.id)])), [initial.chapters, pickIn]);

  return (
    <div className="min-h-screen">
      <FixList
        book={book}
        lines={listed}
        selected={selected}
        ready={ready}
        under={under}
        sort={sort}
        onChooseList={chooseList}
        claude={claude}
        focusSpeaker={focusSpeaker}
        open={listOpen}
        onPick={(line) => {
          select(line, true);
          if (narrow()) setListOpen(false);
        }}
        onClearFocus={() => setFocusSpeaker(null)}
      />

      <CastPanel
        book={book}
        open={castOpen}
        focused={focusSpeaker}
        onFocus={(id) => {
          setFocusSpeaker(id);
          setSelection(null);
          // Their lines are listed on the left.
          if (id && narrow()) setCastOpen(false);
          if (id) setListOpen(true);
          const first = id ? linesOf(id)[0] : undefined;
          if (first) scrollTo(first.chapter, first.segment.id);
        }}
        onChange={saveMember}
      />

      {/* Makes room for the side bars at their pace. */}
      <div
        className={`transition-[padding] duration-300 ease-out motion-reduce:transition-none ${listOpen ? "xl:pl-80" : ""} ${castOpen ? "xl:pr-80" : ""}`}
      >
        <header className="sticky top-0 z-20 bg-bg/85 backdrop-blur-sm">
          {/* Each side bar's button at its own end; the book's name and chapter over the text. */}
          <div className="flex h-12 items-center px-2 text-[13px]">
            <SideToggle side="left" open={listOpen} onClick={toggleList} title="Lines to check  [" />
            <div className="mx-auto flex min-w-0 max-w-[40rem] flex-1 items-center gap-5 px-4">
            <Link href="/" className="font-display text-[20px] capitalize tracking-tight">
              {book.name}
            </Link>
            {/* The chapter showing, as a book's running head; choosing another shows it. */}
            <label className="ml-auto flex min-w-0 cursor-pointer items-center gap-1.5" title="Go to chapter">
              <select
                value={reading}
                onChange={(e) => openChapter(e.target.value)}
                className="min-w-0 max-w-64 cursor-pointer appearance-none truncate bg-transparent py-1 text-right font-display text-[20px] outline-none"
              >
                {book.chapters.map((c) => (
                  <option key={c.id} value={c.id}>
                    {splitTitle(c.title).name}
                  </option>
                ))}
              </select>
              <span className="pointer-events-none text-[10px] text-muted" aria-hidden>
                ▾
              </span>
            </label>
            </div>
            <SideToggle side="right" open={castOpen} onClick={toggleCast} title="Cast  ]" />
          </div>
        </header>

        {error && (
          <p className="mx-auto mt-2 max-w-[40rem] rounded-md bg-red-500/10 px-4 py-2 text-sm text-red-600">{error}</p>
        )}

        <main className="mx-auto max-w-[40rem] px-6 pb-[40vh] pt-16">
          {chapter && (
            <Prose
              key={chapter.id}
              chapter={chapter.id}
              segments={chapter.segments}
              cast={book.cast}
              selected={selected?.chapter === chapter.id ? selected.segment.id : undefined}
              focusSpeaker={focusSpeaker}
              under={under}
              onPick={pickers.get(chapter.id)}
            />
          )}
          <nav className="mt-24 flex items-baseline gap-6 font-display text-[17px] text-muted">
            {prev && (
              <button onClick={() => openChapter(prev.id)} className="min-w-0 truncate text-left hover:text-ink">
                ← {splitTitle(prev.title).name}
              </button>
            )}
            {next && (
              <button onClick={() => openChapter(next.id)} className="ml-auto min-w-0 truncate text-right hover:text-ink">
                {splitTitle(next.title).name} →
              </button>
            )}
          </nav>
        </main>
      </div>

      {selected && (
        <div className={`pointer-events-none fixed inset-x-0 bottom-0 z-30 px-4 pb-6 transition-[left,right] duration-300 ease-out motion-reduce:transition-none ${listOpen ? "xl:left-80" : ""} ${castOpen ? "xl:right-80" : ""}`}>
          <div className="pointer-events-auto">
            <LinePanel
              book={book}
              line={selected}
              likely={likely}
              asking={asking.has(lineKey(selected.chapter, selected.segment.id))}
              searchRef={searchRef}
              onPick={decide}
              onAdd={addCharacter}
              onClose={() => setSelection(null)}
              onClaude={useClaude}
            />
          </div>
        </div>
      )}

    </div>
  );
}

/** Puts a line in view at once, unless it already is: clear of the header
 * above and the line editor below, the page doesn't move. */
function jumpTo(el: HTMLElement) {
  const { top, bottom } = el.getBoundingClientRect();
  if (top >= 64 && bottom <= window.innerHeight - 200) return;
  el.scrollIntoView({ block: "center", behavior: "instant" });
}
