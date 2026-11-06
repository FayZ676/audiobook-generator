"use client";

import { forwardRef, useState } from "react";
import type { CastMember } from "@/lib/model";
import { displayName } from "@/lib/model";
import { SpeakerDot } from "./Prose";

/** Likely speakers as numbered chips, and a search over the whole cast that
 * can add a new character. */
const SpeakerPicker = forwardRef<
  HTMLInputElement,
  {
    likely: string[];
    current: string;
    cast: CastMember[];
    onPick: (id: string) => void;
    onAdd: (name: string) => void;
  }
>(function SpeakerPicker({ likely, current, cast, onPick, onAdd }, searchRef) {
  const [query, setQuery] = useState("");
  const q = query.trim().toLowerCase();
  const matches = q ? cast.filter((m) => m.names.some((n) => n.toLowerCase().includes(q))).slice(0, 6) : [];
  const exact = cast.some((m) => m.names.some((n) => n.toLowerCase() === q));

  const choose = (id: string) => {
    setQuery("");
    onPick(id);
  };

  return (
    <div className="flex flex-wrap items-center gap-1.5">
      {likely.map((id, i) => (
        <button
          key={id}
          onClick={() => choose(id)}
          className={`flex items-center gap-2 rounded-full border px-3 py-1 text-[13px] transition-colors ${
            id === current
              ? "border-ink/80 bg-ink text-bg"
              : "border-line bg-panel hover:border-ink/30"
          }`}
        >
          <SpeakerDot id={id} />
          {displayName(cast, id)}
          {i < 9 && <kbd className={`font-mono text-[10px] ${id === current ? "opacity-60" : "text-muted"}`}>{i + 1}</kbd>}
        </button>
      ))}
      <div className="relative">
        <input
          ref={searchRef}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => {
            e.stopPropagation();
            if (e.key === "Escape") {
              setQuery("");
              e.currentTarget.blur();
            } else if (e.key === "Enter" && q) {
              if (matches[0]) choose(matches[0].id);
              else {
                setQuery("");
                onAdd(query.trim());
              }
            }
          }}
          placeholder="Someone else…  /"
          className="w-44 rounded-full border border-dashed border-line bg-transparent px-3 py-1 text-[13px] outline-none placeholder:text-muted focus:border-solid focus:border-accent"
        />
        {q && (
          <div className="absolute left-0 top-full z-10 mt-1 w-64 overflow-hidden rounded-lg border border-line bg-panel py-1 shadow-lg">
            {matches.map((m) => (
              <button
                key={m.id}
                onClick={() => choose(m.id)}
                className="flex w-full items-center gap-2 px-3 py-1.5 text-left text-[13px] hover:bg-ink/[0.04]"
              >
                <SpeakerDot id={m.id} />
                {m.names[0]}
                {m.names.length > 1 && <span className="truncate text-muted">{m.names.slice(1).join(", ")}</span>}
              </button>
            ))}
            {!exact && (
              <button
                onClick={() => {
                  setQuery("");
                  onAdd(query.trim());
                }}
                className="w-full px-3 py-1.5 text-left text-[13px] text-accent hover:bg-ink/[0.04]"
              >
                + Add “{query.trim()}” as a new character
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
});

export default SpeakerPicker;
