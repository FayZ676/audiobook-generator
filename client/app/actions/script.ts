"use server";

interface Script {
  filename: string;
}

interface BuildScriptRequest {
  narrator_voice_name: string;
  callback_url: string;
}

export async function createScript(formData: FormData) {
  const file = formData.get("file") as File;
  const narrator = formData.get("narrator") as string;

  const request: BuildScriptRequest = {
    narrator_voice_name: narrator,
    callback_url: `${process.env.NEXT_PUBLIC_BASE_URL}/api/webhook`,
  };
  const serverFormData = new FormData();
  serverFormData.append("file", file);
  serverFormData.append("request", JSON.stringify(request));

  try {
    const response = await fetch(
      `${process.env.AUDIOBOOK_SERVICE_URL}/script`,
      { method: "POST", body: serverFormData }
    );
  } catch (error) {
    console.error("Error submitting script:", error);
  }
}

export async function getScripts() {
  const response = await fetch(`${process.env.AUDIOBOOK_SERVICE_URL}/script`);
  const data: Script[] = await response.json();
  return data;
}
