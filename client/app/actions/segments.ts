"use server";

import { getUserId } from "./user";
import { apiCallJson } from "../lib/api";

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
    { cache: "no-store" }
  );
  return data.url;
}
