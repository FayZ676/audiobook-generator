"use client";

import { useMemo } from "react";
import type { Book, CastMember } from "@/lib/model";
import { AGES, GENDERS, NARRATOR_ID } from "@/lib/model";
import { SpeakerDot } from "./Prose";

/** Everyone in the book, most lines first, as a drawer beside the text. A
 * wrong age or gender gives someone the wrong voice for every line, so it's
 * worth a glance. Choosing a character finds their lines in the book. */
export default function CastPanel({
  book,
  focused,
  onFocus,
  onChange,
}: {
  book: Book;
  focused: string | null;
  onFocus: (id: string | null) => void;
  onChange: (member: CastMember) => void;
}) {
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
    <aside className="fixed bottom-0 right-0 top-12 z-40 flex w-[440px] max-w-full flex-col border-l border-line bg-panel shadow-2xl">
      <div className="flex items-center justify-between border-b border-line px-5 py-4">
        <div>
          <h2 className="font-semibold">Cast</h2>
          <p className="text-xs text-muted">
            {book.cast.length - 1} characters
            {unvoiced > 0 && (
              <span className="text-amber-700">
                {" "}
                · {unvoiced === book.cast.length ? "no voices chosen yet" : `${unvoiced} without a voice`}
              </span>
            )}
          </p>
        </div>
      </div>
      <div className="flex-1 overflow-y-auto">
        {members.map((m) => (
          <Member
            key={m.id}
            member={m}
            lines={lines.get(m.id) ?? 0}
            focused={focused === m.id}
            onFocus={() => onFocus(focused === m.id ? null : m.id)}
            onChange={onChange}
          />
        ))}
      </div>
    </aside>
  );
}

function Member({
  member,
  lines,
  focused,
  onFocus,
  onChange,
}: {
  member: CastMember;
  lines: number;
  focused: boolean;
  onFocus: () => void;
  onChange: (m: CastMember) => void;
}) {
  const select = "rounded-md bg-transparent py-0.5 text-xs text-muted outline-none hover:bg-ink/[0.04] focus:bg-ink/[0.04]";
  return (
    <div className={`border-b border-line px-5 py-3 ${focused ? "bg-accent/[0.06]" : ""}`}>
      <div className="flex items-center gap-3">
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
          className="min-w-0 flex-1 rounded-md bg-transparent px-1 py-0.5 text-sm font-medium outline-none hover:bg-ink/[0.04] focus:bg-ink/[0.04]"
        />
        <button
          onClick={onFocus}
          disabled={!lines}
          className={`shrink-0 rounded-full px-2.5 py-0.5 text-xs tabular-nums transition-colors disabled:opacity-40 ${
            focused ? "bg-accent text-white" : "text-muted hover:bg-ink/[0.05] hover:text-ink"
          }`}
          title="Find their lines in the book"
        >
          {lines} {lines === 1 ? "line" : "lines"}
        </button>
      </div>
      <div className="ml-5 mt-1 flex items-center gap-1">
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
        <span className="ml-auto text-xs text-muted">{member.voice ?? "no voice"}</span>
      </div>
    </div>
  );
}
