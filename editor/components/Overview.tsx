import type { Book, Readiness } from "@/lib/model";
import { NARRATOR_ID, READY_AFTER, recheckCost } from "@/lib/model";
import type { Claude, View } from "./BookEditor";

/** What's left to do before the book can be narrated, as short steps. */
export default function Overview({
  book,
  ready,
  claude,
  onOpen,
}: {
  book: Book;
  ready: Readiness;
  claude: Claude;
  onOpen: (v: View) => void;
}) {
  const characters = book.cast.filter((m) => m.id !== NARRATOR_ID);
  const lines = book.chapters.reduce((n, c) => n + c.segments.filter((s) => s.is_dialogue).length, 0);
  const unvoiced = book.cast.filter((m) => m.voice === null).length;
  const cost = recheckCost(book.chapters);
  const progress = claude.bookProgress;

  return (
    <main className="mx-auto max-w-2xl px-6 pb-24 pt-16">
      <h1 className="text-3xl font-semibold capitalize tracking-tight">{book.name}</h1>
      <p className="mt-2 text-sm text-muted">
        {book.chapters.length} chapters · {lines.toLocaleString()} lines of dialogue · {characters.length} characters
      </p>
      <p className="mt-8 text-[15px] leading-7">
        Every line already has a speaker, and most are right. Check the cast, fix the few lines the model got wrong,
        and it&apos;s ready to narrate.
      </p>

      <ol className="mt-10 space-y-3">
        <Step n={1} title="Check the cast" done={false}>
          <p>
            {characters.length} characters. A wrong age or gender gives someone the wrong voice for every line they
            speak, so it&apos;s worth a glance.
          </p>
          {unvoiced > 0 && (
            <p className="mt-2 text-xs text-amber-700 dark:text-amber-300">
              {unvoiced === book.cast.length ? "No voices chosen yet" : `${unvoiced} without a voice yet`}
            </p>
          )}
          <Actions>
            <Button onClick={() => onOpen("Cast")}>Check cast</Button>
          </Actions>
        </Step>

        <Step n={2} title="Fix likely mistakes" done={ready.ready}>
          <p>{fixStatus(ready)}</p>
          {progress ? (
            <div className="mt-4">
              <p className="text-xs">
                Claude Opus is reading chapter {Math.min(progress.done + 1, progress.total)} of {progress.total}…
              </p>
              <div className="mt-2 h-1 overflow-hidden rounded-full bg-line">
                <div
                  className="h-full rounded-full bg-accent transition-[width] duration-500"
                  style={{ width: `${(100 * progress.done) / Math.max(1, progress.total)}%` }}
                />
              </div>
            </div>
          ) : (
            <Actions>
              <Button primary={!ready.ready} onClick={() => onOpen("Fix")}>
                {ready.disagreements > 0
                  ? `Look at ${ready.disagreements} ${ready.disagreements === 1 ? "line" : "lines"}`
                  : ready.reviewed === 0
                    ? "Start"
                    : ready.ready
                      ? "Check more anyway"
                      : "Continue"}
              </Button>
              {ready.unchecked > 0 && (
                <Button onClick={claude.checkBook}>
                  Have Claude Opus check {ready.reviewed > 0 ? "the rest" : "every line"}
                  <span className="ml-1.5 font-normal text-muted">· about ${cost < 0.1 ? cost.toFixed(2) : cost.toFixed(1)}</span>
                </Button>
              )}
            </Actions>
          )}
        </Step>

        <Step n={3} title="Narrate" done={false}>
          <p>{ready.ready ? "The script is ready. Narration is coming soon." : "Once the lines look right. Coming soon."}</p>
        </Step>
      </ol>
    </main>
  );
}

function fixStatus(ready: Readiness): string {
  if (ready.disagreements > 0)
    return `Claude Opus disagreed with ${ready.disagreements} ${ready.disagreements === 1 ? "line" : "lines"}. Those are the likely mistakes; it agreed with the rest it read.`;
  if (ready.ready)
    return ready.unchecked === 0
      ? "Every line has been checked, by you or Claude Opus."
      : `You confirmed the last ${ready.confirmedInARow} lines without changing any, so the rest are very likely right.`;
  if (ready.reviewed === 0)
    return "Go through the lines the model was least sure of, a batch at a time, and stop when you stop finding mistakes. Or have Claude Opus read the book and point out the lines it disagrees with.";
  return (
    `You've checked ${ready.reviewed} lines and fixed ${ready.corrected || "none"}. ` +
    (ready.confirmedInARow > 0
      ? `Once ${READY_AFTER} in a row need no fix (${ready.confirmedInARow} so far), the rest are very likely right.`
      : "Still finding mistakes, so another batch is worth it.")
  );
}

function Step({ n, title, done, children }: { n: number; title: string; done: boolean; children: React.ReactNode }) {
  return (
    <li className="flex gap-5 rounded-xl border border-line bg-panel p-5">
      <span
        className={`flex size-7 shrink-0 items-center justify-center rounded-full text-xs font-semibold ${
          done ? "bg-emerald-600 text-white" : "bg-ink/[0.06] text-muted"
        }`}
      >
        {done ? "✓" : n}
      </span>
      <div className="min-w-0 flex-1 text-sm leading-6 text-muted">
        <h2 className="text-base font-medium text-ink">{title}</h2>
        <div className="mt-1">{children}</div>
      </div>
    </li>
  );
}

function Actions({ children }: { children: React.ReactNode }) {
  return <div className="mt-4 flex flex-wrap gap-2">{children}</div>;
}

function Button({ primary = false, onClick, children }: { primary?: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button
      onClick={onClick}
      className={`h-8 rounded-full px-4 text-[13px] font-medium transition-opacity hover:opacity-90 ${
        primary ? "bg-accent text-white" : "border border-line text-ink"
      }`}
    >
      {children}
    </button>
  );
}
