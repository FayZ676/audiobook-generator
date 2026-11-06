"use server";

import { recheck } from "@/lib/recheck";
import { updateCast, updateSegments } from "@/lib/storage";
import { applyChange, type CastMember, type SegmentChange } from "@/lib/model";

export async function changeSegment(book: string, chapter: string, segmentId: string, change: SegmentChange) {
  await updateSegments(book, chapter, (segments) => {
    const i = segments.findIndex((s) => s.id === segmentId);
    if (i === -1) throw new Error(`No segment ${segmentId} in ${chapter}`);
    // Only the fields a person edits, whatever else the client sends.
    const { speaker_id, reviewed } = change;
    segments[i] = applyChange(segments[i], { speaker_id, reviewed }, new Date().toISOString());
  });
}

/** Save a cast member, adding them if they're new. */
export async function saveCharacter(book: string, member: CastMember) {
  await updateCast(book, (cast) => {
    const i = cast.findIndex((m) => m.id === member.id);
    if (i === -1) cast.push(member);
    else cast[i] = member;
  });
}

/** Ask Claude Opus who speaks these lines of a chapter (or every unreviewed
 * line, given none), and save its answers beside the first ones. */
export async function askClaude(book: string, chapter: string, segmentIds: string[]): Promise<Record<string, string>> {
  const answers = await recheck(book, chapter, segmentIds);
  await updateSegments(book, chapter, (segments) => {
    for (const s of segments) if (answers[s.id]) s.recheck_speaker_id = answers[s.id];
  });
  return answers;
}
