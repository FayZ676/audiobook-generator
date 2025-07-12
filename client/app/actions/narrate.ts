"use server";

import { revalidateTag } from "next/cache";
import { auth } from "@clerk/nextjs/server";

import { getVoices, Voice } from "./voices";

interface NarrationRequest {
  user_id: string;
  script_path: string;
  voices: Voice[];
}

export type NarrationUrl = string;

export async function createNarration(filename?: string) {
  const { userId } = await auth();
  if (!userId) {
    throw new Error("User not authenticated");
  }

  const voices = await getVoices();

  // Use the new multi-chapter path format if filename is provided,
  // otherwise fall back to old format for backward compatibility
  const scriptPath = filename ? `${userId}/${filename}.json` : `${userId}.json`;

  const request: NarrationRequest = {
    user_id: userId,
    script_path: scriptPath,
    voices: voices,
  };

  try {
    await fetch(`${process.env.AUDIOBOOK_SERVICE_URL}/narration`, {
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
    const response = await fetch(
      `${process.env.AUDIOBOOK_SERVICE_URL}/narration/${filename}`,
      {
        cache: "force-cache",
        next: {
          revalidate: 3600,
          tags: ["narration"],
        },
      }
    );
    const narrationUrl = await response.json();
    return narrationUrl;
  } catch (error) {
    console.error("Error fetching narration:", error);
    throw error;
  }
}

export async function deleteNarration(filename: string) {
  try {
    await fetch(`${process.env.AUDIOBOOK_SERVICE_URL}/narration/${filename}`, {
      method: "DELETE",
    });
  } catch (error) {
    console.error("Error deleting narration:", error);
    throw error;
  }
}
