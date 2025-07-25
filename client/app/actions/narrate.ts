"use server";

import { revalidateTag } from "next/cache";
import { auth } from "@clerk/nextjs/server";
import { apiCallVoid, apiCallJson } from "../lib/api";

import { getVoices, Voice } from "./voices";

interface NarrationRequest {
  user_id: string;
  script_path: string;
  voices: Voice[];
}

export type NarrationUrl = string;

export async function createNarration() {
  const { userId } = await auth();
  if (!userId) {
    throw new Error("User not authenticated");
  }

  const voices = await getVoices();

  const request: NarrationRequest = {
    user_id: userId,
    script_path: `${userId}.json`,
    voices: voices,
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

export async function getNarration(): Promise<NarrationUrl | null> {
  const { userId } = await auth();
  if (!userId) {
    throw new Error("User not authenticated");
  }

  const filename = `${userId}.mp3`;
  try {
    const narrationUrl = await apiCallJson(
      `${process.env.AUDIOBOOK_SERVICE_URL}/narration/${filename}`,
      {
        cache: "force-cache",
        next: {
          revalidate: 3600,
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

export async function deleteNarration(filename: string) {
  try {
    await apiCallVoid(
      `${process.env.AUDIOBOOK_SERVICE_URL}/narration/${filename}`,
      {
        method: "DELETE",
      }
    );
  } catch (error) {
    console.error("Error deleting narration:", error);
    throw error;
  }
}
