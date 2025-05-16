"use server";

import { z } from "zod";

const VoiceSchema = z.object({
  name: z.string(),
  age: z.string(),
  gender: z.string(),
  audio_path: z.string(),
  audio_transcript: z.string(),
});

const VoicesSchema = z.array(VoiceSchema);

export type Voice = z.infer<typeof VoiceSchema>;

export async function getVoices(): Promise<Voice[]> {
  try {
    const response = await fetch(`${process.env.AUDIOBOOK_SERVICE_URL}/voices`);
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
