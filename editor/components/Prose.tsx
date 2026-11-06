import type { CastMember, Segment } from "@/lib/model";
import { NARRATOR_ID, displayName, speakerHue } from "@/lib/model";

/** Segments laid out as the book's paragraphs, each line of dialogue tinted
 * in its speaker's colour and tagged with their name. */
export default function Prose({
  segments,
  cast,
  highlight,
  onPick,
  dim = false,
}: {
  segments: Segment[];
  cast: CastMember[];
  highlight?: string;
  onPick?: (segment: Segment) => void;
  dim?: boolean; // context around a highlighted line
}) {
  const paragraphs: Segment[][] = [];
  for (const s of segments) {
    const last = paragraphs.at(-1);
    if (last && last[0].paragraph === s.paragraph) last.push(s);
    else paragraphs.push([s]);
  }
  return (
    <div className="space-y-4 font-serif text-[17px] leading-[1.8]">
      {paragraphs.map((p) => (
        <p key={p[0].id}>
          {p.map((s, i) => (
            <span key={s.id}>
              {i > 0 && " "}
              {s.is_dialogue ? (
                <Line
                  segment={s}
                  name={displayName(cast, s.speaker_id)}
                  showName={i === 0 || p[i - 1].speaker_id !== s.speaker_id || !p[i - 1].is_dialogue}
                  highlighted={s.id === highlight}
                  dim={dim && s.id !== highlight}
                  onPick={onPick}
                />
              ) : (
                <span className={dim ? "text-muted" : ""}>{s.text}</span>
              )}
            </span>
          ))}
        </p>
      ))}
    </div>
  );
}

function Line({
  segment,
  name,
  showName,
  highlighted,
  dim,
  onPick,
}: {
  segment: Segment;
  name: string;
  showName: boolean;
  highlighted: boolean;
  dim: boolean;
  onPick?: (segment: Segment) => void;
}) {
  const hue = speakerHue(segment.speaker_id);
  const narrator = segment.speaker_id === NARRATOR_ID;
  const style = hue === null ? {} : { background: `oklch(var(--tint-l) 0.05 ${hue})` };
  return (
    <span
      id={`line-${segment.id}`}
      onClick={onPick && (() => onPick(segment))}
      className={`rounded-[4px] px-[3px] py-[1px] [box-decoration-break:clone] ${onPick ? "cursor-pointer" : ""} ${
        highlighted ? "outline-2 outline-offset-2 outline-accent" : ""
      } ${dim ? "opacity-55" : ""} ${narrator ? "underline decoration-muted/60 decoration-dashed underline-offset-4" : ""}`}
      style={style}
    >
      {showName && (
        <span className="mr-1 align-[0.15em] font-sans text-[10px] font-semibold uppercase tracking-wider text-muted">
          {name}
        </span>
      )}
      “{segment.text}”
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
