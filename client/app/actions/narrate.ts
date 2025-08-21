"use server";

import { revalidateTag } from "next/cache";

import { getUserId } from "./user";
import { apiCallVoid, apiCallJson } from "../lib/api";

import { getVoices, Voice } from "./voices";

interface NarrationRequest {
  user_id: string;
  voices: Voice[];
  chapter_name: string;
}

export type NarrationUrl = string;

export async function createNarration(chapterName: string) {
  const userId = await getUserId();

  const voices = await getVoices();

  const request: NarrationRequest = {
    user_id: userId,
    voices: voices,
    chapter_name: chapterName,
  };

  try {
    await apiCallVoid(`${process.env.AUDIOBOOK_SERVICE_URL}/narration`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
    });

    revalidateTag("job");
  } catch (error) {
    console.error("Error submitting script:", error);
    throw error;
  }
}

export async function getNarration(
  chapterName: string
): Promise<NarrationUrl | null> {
  const userId = await getUserId();

  try {
    const narrationUrl = await apiCallJson<NarrationUrl>(
      `${process.env.AUDIOBOOK_SERVICE_URL}/narration/${userId}/${chapterName}`,
      {
        cache: "force-cache",
        next: {
          revalidate: 2700,
          tags: ["narration"],
        },
      }
    );
    return narrationUrl;
  } catch (error) {
    console.error("Error fetching narration:", error);
    throw error;
  }
}

export async function deleteNarration(chapterName: string) {
  const userId = await getUserId();

  try {
    await apiCallVoid(
      `${process.env.AUDIOBOOK_SERVICE_URL}/narration/${userId}/${chapterName}`,
      {
        method: "DELETE",
      }
    );
  } catch (error) {
    console.error("Error deleting narration:", error);
    throw error;
  }
}
