"use client";

import { useMemo } from "react";
import type { Book, CastMember } from "@/lib/model";
import { AGES, GENDERS, NARRATOR_ID } from "@/lib/model";
import type { Edits } from "./BookEditor";
import { SpeakerDot } from "./Prose";

/** Everyone in the book, most lines first. A wrong age or gender gives a
 * character the wrong voice for every line, so this is worth checking first. */
export default function CastView({ book, edits }: { book: Book; edits: Edits }) {
  const lines = useMemo(() => {
    const count = new Map<string, number>();
    for (const c of book.chapters)
      for (const s of c.segments) if (s.is_dialogue) count.set(s.speaker_id, (count.get(s.speaker_id) ?? 0) + 1);
    return count;
  }, [book]);
  const members = [...book.cast].sort(
    (a, b) => Number(b.id === NARRATOR_ID) - Number(a.id === NARRATOR_ID) || (lines.get(b.id) ?? 0) - (lines.get(a.id) ?? 0),
  );
  const unvoiced = book.cast.filter((m) => m.voice === null).length;

  return (
    <main className="mx-auto max-w-5xl px-6 pb-24 pt-10">
      <div className="mb-6 flex items-baseline justify-between text-xs text-muted">
        <span>
          {book.cast.length - 1} characters and the narrator · the first name is the one shown
        </span>
        {unvoiced > 0 && <span className="text-amber-700 dark:text-amber-300">{unvoiced} without a voice</span>}
      </div>
      <div className="overflow-hidden rounded-xl border border-line bg-panel">
        <div className="grid grid-cols-[1fr_120px_110px_150px_60px] gap-4 border-b border-line px-5 py-2.5 text-[11px] font-medium uppercase tracking-wider text-muted">
          <span>Names</span>
          <span>Age</span>
          <span>Gender</span>
          <span>Voice</span>
          <span className="text-right">Lines</span>
        </div>
        {members.map((m) => (
          <Member key={m.id} member={m} lines={lines.get(m.id) ?? 0} onChange={edits.saveCharacter} />
        ))}
      </div>
    </main>
  );
}

function Member({ member, lines, onChange }: { member: CastMember; lines: number; onChange: (m: CastMember) => void }) {
  const select = "rounded-md bg-transparent py-1 text-sm outline-none hover:bg-ink/[0.04] focus:bg-ink/[0.04]";
  return (
    <div className="grid grid-cols-[1fr_120px_110px_150px_60px] items-center gap-4 border-b border-line px-5 py-2 last:border-0">
      <span className="flex min-w-0 items-center gap-3">
        <SpeakerDot id={member.id} />
        <input
          // Remount when names change elsewhere, so the field shows them.
          key={member.names.join("|")}
          defaultValue={member.names.join(", ")}
          onBlur={(e) => {
            const names = e.target.value.split(",").map((n) => n.trim()).filter(Boolean);
            if (names.length && names.join("|") !== member.names.join("|")) onChange({ ...member, names });
            else e.target.value = member.names.join(", ");
          }}
          onKeyDown={(e) => e.key === "Enter" && e.currentTarget.blur()}
          className="min-w-0 flex-1 rounded-md bg-transparent px-1.5 py-1 text-sm outline-none hover:bg-ink/[0.04] focus:bg-ink/[0.04]"
        />
      </span>
      <select value={member.age} onChange={(e) => onChange({ ...member, age: e.target.value as CastMember["age"] })} className={select}>
        {AGES.map((a) => (
          <option key={a}>{a}</option>
        ))}
      </select>
      <select
        value={member.gender}
        onChange={(e) => onChange({ ...member, gender: e.target.value as CastMember["gender"] })}
        className={select}
      >
        {GENDERS.map((g) => (
          <option key={g}>{g}</option>
        ))}
      </select>
      <span className="truncate text-sm">
        {member.voice ?? (
          <span className="rounded-md bg-amber-500/15 px-2 py-0.5 text-xs text-amber-800 dark:text-amber-300">No voice</span>
        )}
      </span>
      <span className={`text-right font-mono text-xs tabular-nums ${lines ? "" : "text-muted"}`}>{lines || "—"}</span>
    </div>
  );
}
