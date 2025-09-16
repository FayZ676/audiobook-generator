"use server";

import { revalidateTag } from "next/cache";

import { getUserId } from "./user";
import { apiCallVoid, apiCallJson } from "../lib/api";
import { NarrationEndpointDetails } from "../types";

import { getVoices, Voice } from "./voices";

interface NarrationRequest {
  user_id: string;
  voices: Voice[];
  chapter_name: string;
  endpoint: string;
}

export type NarrationUrl = string;

export async function createNarration(chapterName: string, voices?: Voice[]) {
  const endpointDetails = await getNarrationEndpoint();
  if (!endpointDetails.endpoint) {
    throw new Error(
      "Sorry, not enough resources available to create narration. Please try again later."
    );
  }

  const userId = await getUserId();
  const voicesToUse = voices || await getVoices();

  const request: NarrationRequest = {
    user_id: userId,
    voices: voicesToUse,
    chapter_name: chapterName,
    endpoint: endpointDetails.endpoint,
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

export async function getNarrationEndpoint(): Promise<NarrationEndpointDetails> {
  try {
    const endpointDetails = await apiCallJson<NarrationEndpointDetails>(
      `${process.env.AUDIOBOOK_SERVICE_URL}/narration/endpoint`,
      {
        method: "GET",
      }
    );
    return endpointDetails;
  } catch (error) {
    console.error("Error fetching narration endpoint:", error);
    throw error;
  }
}
