"use server";

import { z } from "zod";
import { revalidateTag } from "next/cache";
import { apiCallJson, apiCall } from "../lib/api";

import { getUserId } from "./user";

import { AgeEnum, GenderEnum } from "../types";

export type Age = z.infer<typeof AgeEnum>;
export type Gender = z.infer<typeof GenderEnum>;

const VoiceSchema = z.object({
  name: z.string(),
  age: AgeEnum,
  gender: GenderEnum,
  audio_path: z.string(),
  audio_transcript: z.string(),
});

const VoicesSchema = z.array(VoiceSchema);

export type Voice = z.infer<typeof VoiceSchema>;

export async function getVoices(): Promise<Voice[]> {
  try {
    const userId = await getUserId();
    const data = await apiCallJson<unknown>(
      `${process.env.AUDIOBOOK_SERVICE_URL}/voices/${userId}`,
      {
        cache: "force-cache",
        next: {
          tags: ["voices"],
        },
      }
    );
    return VoicesSchema.parse(data);
  } catch (error) {
    console.error("Error fetching voices:", error);
    throw error;
  }
}

export async function addVoice(formData: {
  name: string;
  age: Age;
  gender: Gender;
  audio_file: File;
}): Promise<void> {
  try {
    const form = new FormData();
    form.append("user_id", await getUserId());
    form.append("name", formData.name);
    form.append("age", formData.age);
    form.append("gender", formData.gender);
    form.append("audio_file", formData.audio_file);

    await apiCall(`${process.env.AUDIOBOOK_SERVICE_URL}/voices`, {
      method: "POST",
      body: form,
    });

    revalidateTag("voices");
  } catch (error) {
    console.error("Error adding voice:", error);
    throw error;
  }
}

export async function getVoiceAudioUrls(
  voices: Voice[]
): Promise<Record<string, string>> {
  const userId = await getUserId();

  const urlPromises = voices.map((voice) => fetchVoiceAudioUrl(voice, userId));
  const results = await Promise.all(urlPromises);

  return buildAudioUrlsRecord(results);
}

export async function deleteVoice(voiceName: string): Promise<void> {
  try {
    const userId = await getUserId();
    const normalizedVoiceName = voiceName.toLowerCase().replace(/\s+/g, "_");

    await apiCall(
      `${process.env.AUDIOBOOK_SERVICE_URL}/voices/${userId}/${normalizedVoiceName}`,
      {
        method: "DELETE",
      }
    );

    revalidateTag("voices");
  } catch (error) {
    console.error("Error deleting voice:", error);
    throw error;
  }
}

async function fetchVoiceAudioUrl(
  voice: Voice,
  userId: string
): Promise<{ name: string; url: string | null }> {
  const normalizedVoiceName = voice.name.toLowerCase().replace(/\s+/g, "_");

  try {
    const audioUrl = await apiCallJson<string>(
      `${process.env.AUDIOBOOK_SERVICE_URL}/voices/${userId}/${normalizedVoiceName}/audio`,
      {
        cache: "force-cache",
        next: {
          tags: ["voices"],
        },
      }
    );
    return { name: voice.name, url: audioUrl };
  } catch (error) {
    if (error instanceof Error && error.message.includes("404")) {
      return { name: voice.name, url: null };
    }
    console.error(`Error fetching voice audio URL for ${voice.name}:`, error);
    return { name: voice.name, url: null };
  }
}

function buildAudioUrlsRecord(
  results: Array<{ name: string; url: string | null }>
): Record<string, string> {
  const audioUrls: Record<string, string> = {};

  results.forEach(({ name, url }) => {
    if (url) {
      audioUrls[name] = url;
    }
  });

  return audioUrls;
}
