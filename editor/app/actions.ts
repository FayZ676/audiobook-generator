"use server";

import { updateCast, updateSegments } from "@/lib/storage";
import type { CastMember, SegmentChange } from "@/lib/model";

export async function changeSegment(book: string, chapter: string, segmentId: string, change: SegmentChange) {
  await updateSegments(book, chapter, (segments) => {
    const segment = segments.find((s) => s.id === segmentId);
    if (!segment) throw new Error(`No segment ${segmentId} in ${chapter}`);
    // Only the fields a person edits, whatever the client sends.
    if (change.speaker_id !== undefined) segment.speaker_id = change.speaker_id;
    if (change.reviewed !== undefined) segment.reviewed = change.reviewed;
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
