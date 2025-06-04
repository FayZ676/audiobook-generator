"use server";

import { z } from "zod";

// Enum types for voice properties
export const AgeEnum = z.enum(["young", "middle-aged", "old"]);
export const GenderEnum = z.enum(["male", "female"]);

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
    const response = await fetch(
      `${process.env.AUDIOBOOK_SERVICE_URL}/voices`,
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
