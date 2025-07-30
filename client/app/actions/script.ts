"use server";

import { revalidateTag } from "next/cache";
import { getUserId } from "./user";
import { apiCallVoid, apiCallJson } from "../lib/api";

import { z } from "zod";

import { AgeEnum, GenderEnum } from "../types";

const SpeakerDetailsSchema = z.object({
  names: z.array(z.string()),
  age: AgeEnum,
  gender: GenderEnum,
  voice_name: z.string(),
  audio_path: z.string().optional().default(""),
  audio_transcript: z.string().optional().default(""),
});

const ScriptSegmentSchema = z.object({
  text: z.string(),
  speaker_alias: z.string(),
});

const ScriptSchema = z.object({
  segments: z.array(ScriptSegmentSchema),
  speakers: z.array(SpeakerDetailsSchema),
});

interface BuildScriptRequest {
  user_id: string;
  text_content: string;
  chapter_name: string;
}

interface CreateScriptProps {
  textContent: string;
  chapterName: string;
}

interface UpdateScriptProps {
  script: Script;
  chapterName: string;
}

export type Script = z.infer<typeof ScriptSchema>;

export async function createScript({
  textContent,
  chapterName: chapterName,
}: CreateScriptProps) {
  const userId = await getUserId();

  const request: BuildScriptRequest = {
    user_id: userId,
    text_content: textContent,
    chapter_name: chapterName,
  };

  try {
    await apiCallVoid(`${process.env.AUDIOBOOK_SERVICE_URL}/script`, {
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

export async function getScript(chapterName: string): Promise<Script | null> {
  const userId = await getUserId();

  const rawData = await apiCallJson<unknown>(
    `${process.env.AUDIOBOOK_SERVICE_URL}/script/${userId}/${chapterName}`,
    {
      cache: "force-cache",
      next: {
        tags: ["script"],
      },
    }
  );
  if (rawData === null) {
    return null;
  }
  const result = ScriptSchema.safeParse(rawData);
  if (!result.success) {
    console.error("Validation error:", result.error.format());
    throw new Error("Invalid API response: schema validation failed");
  }

  return result.data;
}

export async function deleteScript(chapterName: string) {
  const userId = await getUserId();

  await apiCallVoid(
    `${process.env.AUDIOBOOK_SERVICE_URL}/script/${userId}/${chapterName}`,
    {
      method: "DELETE",
    }
  );
}

export async function updateScript({
  script,
  chapterName: chapterName,
}: UpdateScriptProps) {
  const userId = await getUserId();

  const data = await apiCallJson<unknown>(
    `${process.env.AUDIOBOOK_SERVICE_URL}/script/${userId}/${chapterName}`,
    {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ script }),
    }
  );

  revalidateTag("script");

  return data;
}
