"use server";

import { auth } from "@clerk/nextjs/server";

import { getVoices, Voice } from "./voices";

interface NarrationRequest {
  script_path: string;
  voices: Voice[];
}

export interface Narration {
  audioUrl: string;
  contentType: string;
  filename: string;
}

export async function createNarration() {
  const { userId } = await auth();
  if (!userId) {
    throw new Error("User not authenticated");
  }

  const voices = await getVoices();

  // TODO: We should just need to send the user id and not add the json suffix.
  const request: NarrationRequest = {
    script_path: `${userId}.json`,
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
  } catch (error) {
    console.error("Error submitting script:", error);
    throw error;
  }
}

export async function getNarration(): Promise<Narration> {
  const { userId } = await auth();
  if (!userId) {
    throw new Error("User not authenticated");
  }

  try {
    const response = await fetch(
      `${process.env.AUDIOBOOK_SERVICE_URL}/narration/${userId}`
    );

    const blob = await response.blob();
    const audioUrl = URL.createObjectURL(blob);

    return {
      audioUrl,
      contentType: response.headers.get("content-type") || "audio/mpeg",
      filename:
        response.headers
          .get("content-disposition")
          ?.split("filename=")[1]
          ?.replace(/"/g, "") || `narration_${userId}.mp3`,
    };
  } catch (error) {
    console.error("Error fetching narration:", error);
    throw error;
  }
}

export async function deleteNarration() {}
