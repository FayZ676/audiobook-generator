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
});

const ScriptSegmentSchema = z.object({
  text: z.string(),
  speaker_alias: z.string(),
  voice_name: z.string(),
});

const LegacyScriptSegmentSchema = z.object({
  voice_name: z.string(),
  speaker: SpeakerDetailsSchema,
  text: z.string(),
});

const NewScriptSchema = z.object({
  segments: z.array(ScriptSegmentSchema),
  speakers: z.array(SpeakerDetailsSchema),
  voices: z.record(z.string()),
});

const LegacyScriptSchema = z.array(LegacyScriptSegmentSchema);

const ScriptResponseSchema = z.union([NewScriptSchema, LegacyScriptSchema]);

interface BuildScriptRequest {
  user_id: string;
  text_content: string;
  narrator_voice_name: string;
}

interface DeleteScriptRequest {
  filename: string;
}

interface CreateScriptProps {
  textContent: string;
  narrator: string;
}

interface UpdateScriptProps {
  script: Script | LegacyScript;
}

export type Script = z.infer<typeof NewScriptSchema>;
export type LegacyScript = z.infer<typeof LegacyScriptSchema>;
export type ScriptResponse = z.infer<typeof ScriptResponseSchema>;

// Helper function to normalize script format
export function normalizeScript(scriptResponse: ScriptResponse): Script {
  if (Array.isArray(scriptResponse)) {
    // Legacy format - convert to new format
    const segmentMap = new Map<string, { speaker: typeof scriptResponse[0]["speaker"], voice: string }>();
    const segments = scriptResponse.map(segment => {
      const speakerAlias = segment.speaker.names[0];
      segmentMap.set(speakerAlias, { speaker: segment.speaker, voice: segment.voice_name });
      return {
        text: segment.text,
        speaker_alias: speakerAlias,
        voice_name: segment.voice_name,
      };
    });
    
    const speakers = Array.from(segmentMap.values()).map(entry => entry.speaker);
    const voices = Object.fromEntries(
      Array.from(segmentMap.entries()).map(([alias, entry]) => [alias, entry.voice])
    );
    
    return {
      segments,
      speakers,
      voices,
    };
  } else {
    // New format - return as is
    return scriptResponse;
  }
}

export async function createScript({ textContent, narrator }: CreateScriptProps) {
  const { userId } = await auth();
  if (!userId) {
    throw new Error("User not authenticated");
  }

  const request: BuildScriptRequest = {
    user_id: userId,
    text_content: textContent,
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
  
  // Normalize to new format
  return normalizeScript(result.data);
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
