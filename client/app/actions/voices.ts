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

export async function getVoiceAudioUrl(voiceName: string): Promise<string> {
  const userId = await getUserId();
  const normalizedVoiceName = voiceName.toLowerCase().replace(/\s+/g, "_");

  const audioUrl = await apiCallJson<string>(
    `${process.env.AUDIOBOOK_SERVICE_URL}/voices/${userId}/${normalizedVoiceName}/audio`,
    {
      cache: "force-cache",
      next: {
        tags: ["voices"],
      },
    }
  );
  return audioUrl;
}

export async function deleteVoice(voiceName: string): Promise<void> {
  const userId = await getUserId();

  await apiCall(
    `${process.env.AUDIOBOOK_SERVICE_URL}/voices/${userId}/${voiceName}`,
    {
      method: "DELETE",
      cache: "no-cache",
      next: {
        tags: ["voices"],
      },
    }
  );

  revalidateTag("voices");
}
