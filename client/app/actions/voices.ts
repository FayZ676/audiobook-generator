"use server";

import { z } from "zod";

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
    const response = await fetch(
      `${process.env.AUDIOBOOK_SERVICE_URL}/voices/${userId}`,
      {
        cache: "force-cache",
        next: {
          tags: ["voices"],
        },
      }
    );
    if (!response.ok) {
      throw new Error("Failed to fetch voices");
    }
    const data = await response.json();
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
  audio_transcript: string;
  audio_file: File;
}): Promise<void> {
  try {
    const form = new FormData();
    form.append("user_id", await getUserId());
    form.append("name", formData.name);
    form.append("age", formData.age);
    form.append("gender", formData.gender);
    form.append("audio_transcript", formData.audio_transcript);
    form.append("audio_file", formData.audio_file);

    const response = await fetch(
      `${process.env.AUDIOBOOK_SERVICE_URL}/voices`,
      {
        method: "POST",
        body: form,
      }
    );

    if (!response.ok) {
      throw new Error("Failed to add voice");
    }
  } catch (error) {
    console.error("Error adding voice:", error);
    throw error;
  }
}
