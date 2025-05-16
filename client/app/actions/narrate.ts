"use server";

import { auth } from "@clerk/nextjs/server";

import { getVoices, Voice } from "./voices";

interface NarrationRequest {
  script_path: string;
  voices: Voice[];
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

export async function getNarration() {
  console.log("Fetching narration");
}

export async function deleteNarration() {}
