import type { Book, Readiness } from "@/lib/model";
import { NARRATOR_ID, READY_AFTER } from "@/lib/model";
import type { View } from "./BookEditor";

/** What's left to do before the book can be narrated, as two short steps. */
export default function Overview({ book, ready, onOpen }: { book: Book; ready: Readiness; onOpen: (v: View) => void }) {
  const characters = book.cast.filter((m) => m.id !== NARRATOR_ID);
  const lines = book.chapters.reduce((n, c) => n + c.segments.filter((s) => s.is_dialogue).length, 0);
  const unvoiced = book.cast.filter((m) => m.voice === null).length;

  const fixStatus =
    ready.reviewed === 0
      ? "You'll see the lines the model was least sure of, a batch at a time. Most mistakes are among them. Stop when you stop finding any."
      : ready.ready
        ? `You confirmed the last ${ready.confirmedInARow} lines without changing any, so the rest are very likely right.`
        : `You've checked ${ready.reviewed} lines and fixed ${ready.corrected || "none"}. ` +
          (ready.confirmedInARow > 0
            ? `Once ${READY_AFTER} in a row need no fix (${ready.confirmedInARow} so far), the rest are very likely right.`
            : "Still finding mistakes, so another batch is worth it.");

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
        <Step
          n={1}
          title="Check the cast"
          body={`${characters.length} characters. A wrong age or gender gives someone the wrong voice for every line they speak, so it's worth a glance.`}
          note={
            unvoiced === book.cast.length
              ? "No voices chosen yet"
              : unvoiced
                ? `${unvoiced} without a voice yet`
                : undefined
          }
          action="Check cast"
          onClick={() => onOpen("Cast")}
        />
        <Step
          n={2}
          title="Fix likely mistakes"
          body={fixStatus}
          done={ready.ready}
          action={ready.reviewed === 0 ? "Start" : ready.ready ? "Check more anyway" : "Continue"}
          primary={!ready.ready}
          onClick={() => onOpen("Fix")}
        />
        <Step
          n={3}
          title="Narrate"
          body={ready.ready ? "The script is ready. Narration is coming soon." : "Once the lines look right. Coming soon."}
        />
      </ol>
    </main>
  );
}

function Step({
  n,
  title,
  body,
  note,
  action,
  onClick,
  done = false,
  primary = false,
}: {
  n: number;
  title: string;
  body: string;
  note?: string;
  action?: string;
  onClick?: () => void;
  done?: boolean;
  primary?: boolean;
}) {
  return (
    <li className="flex gap-5 rounded-xl border border-line bg-panel p-5">
      <span
        className={`flex size-7 shrink-0 items-center justify-center rounded-full text-xs font-semibold ${
          done ? "bg-emerald-600 text-white" : "bg-ink/[0.06] text-muted"
        }`}
      >
        {done ? "✓" : n}
      </span>
      <div className="min-w-0 flex-1">
        <h2 className="font-medium">{title}</h2>
        <p className="mt-1 text-sm leading-6 text-muted">{body}</p>
        {note && <p className="mt-2 text-xs text-amber-700 dark:text-amber-300">{note}</p>}
      </div>
      {action && (
        <button
          onClick={onClick}
          className={`h-8 shrink-0 self-center rounded-full px-4 text-[13px] font-medium transition-opacity hover:opacity-90 ${
            primary ? "bg-accent text-white" : "border border-line"
          }`}
        >
          {action}
        </button>
      )}
    </li>
  );
}
