"use server";

import { auth, currentUser } from "@clerk/nextjs/server";

export interface Script {
  filename: string;
}

interface BuildScriptRequest {
  user_id: string;
  filename: string;
  narrator_voice_name: string;
  callback_url: string;
}

interface DeleteScriptRequest {
  filename: string;
}

export async function createScript(formData: FormData) {
  const filename = formData.get("filename") as string;
  const narrator = formData.get("narrator") as string;
  const { userId } = await auth();

  if (!userId) {
    throw new Error("User not authenticated");
  }

  const request: BuildScriptRequest = {
    user_id: userId,
    filename: filename,
    narrator_voice_name: narrator,
    callback_url: `${process.env.CLIENT_URL}/api/webhook`,
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

export async function getScripts() {
  const { userId } = await auth();

  if (!userId) {
    throw new Error("User not authenticated");
  }

  const response = await fetch(
    `${process.env.AUDIOBOOK_SERVICE_URL}/script?user_id=${userId}`
  );
  const data: Script[] = await response.json();
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
