"use client";

import type { Book, Readiness } from "@/lib/model";
import { READY_AFTER, displayName, recheckCost } from "@/lib/model";
import type { Claude } from "./BookEditor";
import { SpeakerDot } from "./Prose";

/** The few things to do with the book, in one quiet bar. */
export default function ControlBar({
  book,
  ready,
  claude,
  focusSpeaker,
  onNext,
  onClearFocus,
  onCast,
}: {
  book: Book;
  ready: Readiness;
  claude: Claude;
  focusSpeaker: string | null;
  onNext: () => void;
  onClearFocus: () => void;
  onCast: () => void;
}) {
  const progress = claude.bookProgress;
  const cost = recheckCost(book.chapters);
  const pill = "flex h-8 items-center gap-2 rounded-full px-3.5 text-[13px] transition-colors";
  return (
    <div className="mx-auto flex w-fit max-w-full flex-wrap items-center gap-1 rounded-full border border-line bg-panel/90 p-1 shadow-[0_8px_30px_-10px_rgba(0,0,0,0.25)] backdrop-blur">
      {focusSpeaker ? (
        <>
          <span className={`${pill} bg-accent/10`}>
            <SpeakerDot id={focusSpeaker} />
            {displayName(book.cast, focusSpeaker)}&apos;s lines
            <button onClick={onClearFocus} className="ml-1 text-muted hover:text-ink" title="Show everyone">
              ✕
            </button>
          </span>
          <button onClick={onNext} className={`${pill} hover:bg-ink/[0.05]`}>
            Next line <Kbd>N</Kbd>
          </button>
        </>
      ) : ready.ready ? (
        <span className={`${pill} text-emerald-700 dark:text-emerald-400`}>
          <span className="size-1.5 rounded-full bg-current" /> Ready to narrate
        </span>
      ) : (
        <button onClick={onNext} className={`${pill} bg-accent font-medium text-white hover:opacity-90`}>
          Next likely mistake <Kbd light>N</Kbd>
        </button>
      )}

      {!focusSpeaker && ready.reviewed > 0 && !ready.ready && (
        <span className={`${pill} text-muted`} title={`${READY_AFTER} in a row means the rest are very likely right`}>
          {ready.corrected} fixed · {ready.confirmedInARow}/{READY_AFTER} right in a row
        </span>
      )}

      <button onClick={onCast} className={`${pill} hover:bg-ink/[0.05]`}>
        Cast <Kbd>C</Kbd>
      </button>

      {progress ? (
        <span className={`${pill} text-muted`}>
          <span className="size-3 animate-spin rounded-full border-2 border-accent border-t-transparent" />
          Claude is reading chapter {Math.min(progress.done + 1, progress.total)} of {progress.total}
        </span>
      ) : (
        ready.unchecked > 0 && (
          <button onClick={claude.checkBook} className={`${pill} hover:bg-ink/[0.05]`} title="Claude Opus reads each chapter and points out lines it disagrees with">
            <span className="text-accent">✦</span> Check with Claude
            <span className="text-muted">~${cost < 0.1 ? cost.toFixed(2) : cost.toFixed(1)}</span>
          </button>
        )
      )}
    </div>
  );
}

function Kbd({ children, light = false }: { children: React.ReactNode; light?: boolean }) {
  return (
    <kbd className={`rounded border px-1 font-mono text-[10px] ${light ? "border-white/40 text-white/80" : "border-line text-muted"}`}>
      {children}
    </kbd>
  );
}
