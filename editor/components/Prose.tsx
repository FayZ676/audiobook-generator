import { memo } from "react";
import type { CastMember, Segment } from "@/lib/model";
import { NARRATOR_ID, displayName, mark, percent, speakerHue } from "@/lib/model";

/** A chapter's segments laid out as its paragraphs, each line of dialogue
 * tinted in its speaker's colour and tagged with their name. Lines worth a
 * look carry a small mark. */
function Prose({
  chapter,
  segments,
  cast,
  selected,
  focusSpeaker,
  under,
  onPick,
}: {
  chapter: string;
  segments: Segment[];
  cast: CastMember[];
  selected?: string; // segment id
  focusSpeaker?: string | null; // other speakers' lines fade
  under: number; // lines less sure than this are marked
  onPick?: (segment: Segment) => void;
}) {
  const paragraphs: Segment[][] = [];
  for (const s of segments) {
    const last = paragraphs.at(-1);
    if (last && last[0].paragraph === s.paragraph) last.push(s);
    else paragraphs.push([s]);
  }
  // The chapter's title is its first paragraph; the header shows it, so it's left out here.
  const first = paragraphs[0];
  const title = first?.length === 1 && !first[0].is_dialogue ? first[0] : null;
  const body = title ? paragraphs.slice(1) : paragraphs;
  return (
    <div className="font-serif text-[18px] leading-[1.9] text-ink/90">
      {body.map((p, n) => (
        <p
          key={p[0].id}
          className={`mt-6 first-of-type:mt-0 ${
            n === 0 && !p[0].is_dialogue
              ? "first-letter:float-left first-letter:mr-2 first-letter:mt-1 first-letter:font-display first-letter:text-[3.6em] first-letter:leading-[0.8] first-letter:text-accent"
              : ""
          }`}
        >
          {p.map((s, i) => (
            <span key={s.id}>
              {i > 0 && " "}
              {s.is_dialogue ? (
                <Line
                  id={`line-${chapter}-${s.id}`}
                  segment={s}
                  name={displayName(cast, s.speaker_id)}
                  showName={i === 0 || p[i - 1].speaker_id !== s.speaker_id || !p[i - 1].is_dialogue}
                  selected={s.id === selected}
                  faded={!!focusSpeaker && s.speaker_id !== focusSpeaker}
                  under={under}
                  onPick={onPick}
                />
              ) : (
                <span className={focusSpeaker ? "opacity-45" : ""}>{s.text}</span>
              )}
            </span>
          ))}
        </p>
      ))}
    </div>
  );
}

export default memo(Prose);

function Line({
  id,
  segment,
  name,
  showName,
  selected,
  faded,
  under,
  onPick,
}: {
  id: string;
  segment: Segment;
  name: string;
  showName: boolean;
  selected: boolean;
  faded: boolean;
  under: number;
  onPick?: (segment: Segment) => void;
}) {
  const hue = speakerHue(segment.speaker_id);
  const narrator = segment.speaker_id === NARRATOR_ID;
  const style = hue === null || faded ? {} : { background: `oklch(var(--tint-l) 0.05 ${hue})` };
  return (
    <span
      id={id}
      onClick={onPick && (() => onPick(segment))}
      className={`scroll-my-40 rounded-[4px] px-[3px] py-[1px] [box-decoration-break:clone] transition-[outline-color] ${
        onPick ? "cursor-pointer hover:outline hover:outline-1 hover:outline-offset-2 hover:outline-ink/20" : ""
      } ${selected ? "!outline-2 !outline-offset-2 !outline-accent" : ""} ${faded ? "opacity-45" : ""} ${
        narrator ? "underline decoration-muted/60 decoration-dashed underline-offset-4" : ""
      }`}
      style={style}
    >
      <Mark kind={mark(segment, under)} sure={percent(segment)} />
      {showName && (
        <span className="mr-1 align-[0.15em] font-sans text-[10px] font-semibold uppercase tracking-wider text-muted">
          {name}
        </span>
      )}
      “{segment.text}”
    </span>
  );
}

/** A quiet sign before a line: Claude disagrees, the model was unsure, or a
 * person fixed it. */
function Mark({ kind, sure }: { kind: ReturnType<typeof mark>; sure: number }) {
  if (kind === null) return null;
  const look = {
    disagrees: { text: "✦", className: "text-accent", title: "Claude Opus disagrees" },
    unsure: { text: "●", className: "text-amber-500 text-[8px]", title: `The model was ${sure}% sure` },
    fixed: { text: "✎", className: "text-muted", title: "You fixed this" },
  }[kind];
  return (
    <span title={look.title} className={`mr-1 inline-block align-[0.2em] font-sans text-[11px] ${look.className}`}>
      {look.text}
    </span>
  );
}

/** A dot in the speaker's colour; the narrator's is hollow. */
export function SpeakerDot({ id }: { id: string }) {
  const hue = speakerHue(id);
  return (
    <span
      className="inline-block size-2 shrink-0 rounded-full"
      style={hue === null ? { boxShadow: "inset 0 0 0 1.5px var(--muted)" } : { background: `oklch(var(--dot-l) 0.14 ${hue})` }}
    />
  );
}
