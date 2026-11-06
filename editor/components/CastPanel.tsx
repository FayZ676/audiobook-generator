"use client";

import { useMemo } from "react";
import type { Book, CastMember } from "@/lib/model";
import { AGES, GENDERS, NARRATOR_ID, displayName } from "@/lib/model";
import { SpeakerDot } from "./Prose";
import SidePanel, { SideRow } from "./SidePanel";

/** Everyone in the book, most lines first. Choosing someone lists their lines
 * on the left and opens their details here: a wrong age or gender gives them
 * the wrong voice for every line, so it's worth a glance. */
export default function CastPanel({
  book,
  open,
  focused,
  onFocus,
  onChange,
}: {
  book: Book;
  open: boolean;
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
    <SidePanel
      side="right"
      open={open}
      head={
        <>
          <span className="flex-1">{book.cast.length - 1} characters</span>
          {unvoiced > 0 && (
            <span className="text-amber-700">{unvoiced === book.cast.length ? "no voices yet" : `${unvoiced} without a voice`}</span>
          )}
        </>
      }
    >
      {members.map((m) => {
        const chosen = focused === m.id;
        return (
          <SideRow
            key={m.id}
            chosen={chosen}
            onClick={() => onFocus(chosen ? null : m.id)}
            below={chosen && <Details member={m} onChange={onChange} />}
          >
            <SpeakerDot id={m.id} />
            <span className="min-w-0 flex-1 truncate font-serif text-[13px] text-ink/80">{displayName(book.cast, m.id)}</span>
            <span className="text-[11px] tabular-nums text-muted">{lines.get(m.id) ?? 0}</span>
          </SideRow>
        );
      })}
    </SidePanel>
  );
}

/** A chosen character's names, age, gender and voice. */
function Details({ member, onChange }: { member: CastMember; onChange: (m: CastMember) => void }) {
  const field = "rounded bg-transparent py-0.5 text-xs text-muted outline-none hover:bg-ink/[0.04] focus:bg-ink/[0.04] focus:text-ink";
  return (
    <div className="space-y-1 pb-1.5 pl-[18px] pt-1">
      <input
        // Remount when names change elsewhere, so the field shows them.
        key={member.names.join("|")}
        defaultValue={member.names.join(", ")}
        title="Names, separated by commas; the first is the one shown"
        onBlur={(e) => {
          const names = e.target.value.split(",").map((n) => n.trim()).filter(Boolean);
          if (names.length && names.join("|") !== member.names.join("|")) onChange({ ...member, names });
          else e.target.value = member.names.join(", ");
        }}
        onKeyDown={(e) => {
          e.stopPropagation();
          if (e.key === "Enter") e.currentTarget.blur();
        }}
        className={`${field} w-full px-1`}
      />
      <div className="flex items-center gap-1">
        <select value={member.age} onChange={(e) => onChange({ ...member, age: e.target.value as CastMember["age"] })} className={field}>
          {AGES.map((a) => (
            <option key={a}>{a}</option>
          ))}
        </select>
        <select
          value={member.gender}
          onChange={(e) => onChange({ ...member, gender: e.target.value as CastMember["gender"] })}
          className={field}
        >
          {GENDERS.map((g) => (
            <option key={g}>{g}</option>
          ))}
        </select>
        <span className="ml-auto truncate text-xs text-muted">{member.voice ?? "no voice"}</span>
      </div>
    </div>
  );
}
