"use server";

import { revalidateTag } from "next/cache";
import { auth } from "@clerk/nextjs/server";
import { getUserId } from "./user";

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
  filename: string;
  character_voice_mappings?: CharacterVoiceMappings;
}

interface DeleteScriptRequest {
  filename: string;
}

interface CreateScriptProps {
  textContent: string;
  filename: string;
  characterVoiceMappings?: CharacterVoiceMappings;
}

export type Script = z.infer<typeof ScriptSchema>;
export type CharacterVoiceMappings = Record<string, string>;

export async function createScript({
  textContent,
  filename,
  characterVoiceMappings,
}: CreateScriptProps) {
  const { userId } = await auth();
  if (!userId) {
    throw new Error("User not authenticated");
  }

  const request: BuildScriptRequest = {
    user_id: userId,
    text_content: textContent,
    filename,
    character_voice_mappings: characterVoiceMappings,
  };

  try {
    await fetch(`${process.env.AUDIOBOOK_SERVICE_URL}/script`, {
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

export async function getScript(): Promise<Script | null> {
  const { userId } = await auth();

  if (!userId) {
    throw new Error("User not authenticated");
  }

  const filename = `${userId}.json`;
  const response = await fetch(
    `${process.env.AUDIOBOOK_SERVICE_URL}/script/${filename}`,
    {
      cache: "force-cache",
      next: {
        tags: ["script"],
      },
    }
  );
  const rawData = await response.json();
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

interface ScriptInfo {
  filename: string;
  s3_key: string;
}

export async function listUserScripts(): Promise<ScriptInfo[]> {
  const { userId } = await auth();

  if (!userId) {
    throw new Error("User not authenticated");
  }

  const response = await fetch(
    `${process.env.AUDIOBOOK_SERVICE_URL}/scripts/${userId}`,
    {
      cache: "force-cache",
      next: {
        tags: ["script"],
      },
    }
  );
  
  if (!response.ok) {
    throw new Error("Failed to fetch user scripts");
  }
  
  return response.json();
}

export async function getUserScript(filename: string): Promise<Script | null> {
  const { userId } = await auth();

  if (!userId) {
    throw new Error("User not authenticated");
  }

  const response = await fetch(
    `${process.env.AUDIOBOOK_SERVICE_URL}/script/${userId}/${filename}`,
    {
      cache: "force-cache",
      next: {
        tags: ["script"],
      },
    }
  );
  
  const rawData = await response.json();
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

export async function deleteScript(filename: string) {
  const { userId } = await auth();
  if (!userId) {
    throw new Error("User not authenticated");
  }

  await fetch(`${process.env.AUDIOBOOK_SERVICE_URL}/script/${userId}/${filename}`, {
    method: "DELETE",
    headers: {
      "Content-Type": "application/json",
    },
  });
  revalidateTag("script");
}

export async function updateScript(filename: string, script: Script) {
  const { userId } = await auth();
  if (!userId) {
    throw new Error("User not authenticated");
  }

  const response = await fetch(
    `${process.env.AUDIOBOOK_SERVICE_URL}/script/${userId}/${filename}`,
    {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ script }),
    }
  );

  if (!response.ok) {
    throw new Error("Failed to update script");
  }

  revalidateTag("script");

  return response.json();
}
