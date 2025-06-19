"use server";

import { revalidateTag } from "next/cache";
import { auth } from "@clerk/nextjs/server";
import { getUserId } from "./user";

import { z } from "zod";

import { uploadTextFile } from "./file";
import { AgeEnum, GenderEnum } from "../types";

const SpeakerDetailsSchema = z.object({
  names: z.array(z.string()),
  age: AgeEnum,
  gender: GenderEnum,
});

const ScriptSegmentSchema = z.object({
  voice_name: z.string(),
  speaker: SpeakerDetailsSchema,
  text: z.string(),
});

const ScriptResponseSchema = z.array(ScriptSegmentSchema);

interface BuildScriptRequest {
  user_id: string;
  filename: string;
  narrator_voice_name: string;
}

interface DeleteScriptRequest {
  filename: string;
}

interface CreateScriptProps {
  file: File;
  narrator: string;
}

interface UpdateScriptProps {
  script: Script;
}

export type Script = z.infer<typeof ScriptResponseSchema>;

export async function createScript({ file, narrator }: CreateScriptProps) {
  const { userId } = await auth();
  if (!userId) {
    throw new Error("User not authenticated");
  }

  const filename = await uploadTextFile(file);
  const request: BuildScriptRequest = {
    user_id: userId,
    filename: filename,
    narrator_voice_name: narrator,
  };

  try {
    await fetch(`${process.env.AUDIOBOOK_SERVICE_URL}/script`, {
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
  const result = ScriptResponseSchema.safeParse(rawData);
  if (!result.success) {
    console.error("Validation error:", result.error.format());
    throw new Error("Invalid API response: schema validation failed");
  }
  return result.data;
}

export async function deleteScript(filename: string) {
  const request: DeleteScriptRequest = {
    filename: filename,
  };
  await fetch(`${process.env.AUDIOBOOK_SERVICE_URL}/script/${filename}`, {
    method: "DELETE",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });
}

export async function updateScript({ script }: UpdateScriptProps) {
  const userId = await getUserId();

  const filename = `${userId}.json`;
  const response = await fetch(`${process.env.AUDIOBOOK_SERVICE_URL}/script/${filename}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ script }),
  });

  if (!response.ok) {
    throw new Error("Failed to update script");
  }
  
  revalidateTag("script");
  
  return response.json();
}
