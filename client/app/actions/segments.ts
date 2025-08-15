"use server";

import { revalidateTag } from "next/cache";
import { getUserId } from "./user";
import { apiCallJson, apiCallVoid } from "../lib/api";
import { getVoices } from "./voices";

export interface SegmentAudio {
  id: string;
  index: number;
  key: string;
  url: string;
}

export interface AudioManifest {
  narration: { key: string; url: string };
  segments: SegmentAudio[];
}

export async function getAudioManifest(
  chapterName: string
): Promise<AudioManifest> {
  const userId = await getUserId();
  return apiCallJson<AudioManifest>(
    `${process.env.AUDIOBOOK_SERVICE_URL}/narration/${userId}/${chapterName}/audio`,
    {
      cache: "force-cache",
      next: { revalidate: 3600, tags: ["audio-manifest"] },
    }
  );
}

export async function getSegmentAudioUrl(
  chapterName: string,
  segmentId: string
): Promise<string> {
  const userId = await getUserId();
  const data = await apiCallJson<{ key: string; url: string }>(
    `${process.env.AUDIOBOOK_SERVICE_URL}/narration/${userId}/${chapterName}/segments/${segmentId}`,
    {
      cache: "force-cache",
      next: { revalidate: 3600, tags: [`segment-audio-${segmentId}`] },
    }
  );
  return data.url;
}

export async function regenerateSegment(
  chapterName: string,
  segmentId: string
): Promise<void> {
  const userId = await getUserId();
  const voices = await getVoices();
  await apiCallVoid(`${process.env.AUDIOBOOK_SERVICE_URL}/narration`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_id: userId,
      voices,
      chapter_name: chapterName,
      segment_ids: [segmentId],
    }),
  });
  revalidateTag("job");
}
