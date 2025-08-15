import { z } from "zod";

export const AgeEnum = z.enum(["young", "middle-aged", "old"]);
export const GenderEnum = z.enum(["male", "female"]);

export const ManualCharacterSchema = z.object({
  name: z.string(),
  age: AgeEnum,
  gender: GenderEnum,
});

export type ManualCharacter = z.infer<typeof ManualCharacterSchema>;

export interface AudioSegmentData {
  ids: string[];
  urls: Record<string, string>;
}

export interface VoiceAudioData {
  urls: Record<string, string>;
}
