"use server";

import { auth } from "@clerk/nextjs/server";

import { uploadTextFile } from "./file";

export interface SpeakerDetails {
  names: string[];
  age: string;
  gender: string;
}

export interface Script {
  voice_name: string;
  speaker: SpeakerDetails;
  text: string;
}

interface BuildScriptRequest {
  user_id: string;
  filename: string;
  narrator_voice_name: string;
}

interface DeleteScriptRequest {
  filename: string;
}

export async function createScript(formData: FormData) {
  const file = formData.get("file") as File;
  const narrator = formData.get("narrator") as string;
  const { userId } = await auth();

  if (!userId) {
    throw new Error("User not authenticated");
  }

  const response = await uploadTextFile(file);
  const filename = await response.text();

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

export async function getScript() {
  const { userId } = await auth();

  if (!userId) {
    throw new Error("User not authenticated");
  }

  const response = await fetch(
    `${process.env.AUDIOBOOK_SERVICE_URL}/script/${userId}`
  );
  const data: Script = await response.json();
  return data;
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
