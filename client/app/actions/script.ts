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
  const requestBody: BuildScriptRequest = {
    narrator_voice_name: narrator,
    callback_url: `${process.env.NEXT_PUBLIC_BASE_URL}/api/webhook`,
  };

  const serverFormData = new FormData();
  serverFormData.append("file", file);
  serverFormData.append("request", JSON.stringify(requestBody));

  fetch(
    `${process.env.AUDIOBOOK_SERVICE_URL}/script?narrator=${encodeURIComponent(
      narrator
    )}`,
    {
      method: "POST",
      body: serverFormData,
      headers: {
        "Content-Type": "application/json",
      },
    }
  )
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}

export async function getScripts() {
  const response = await fetch(`${process.env.AUDIOBOOK_SERVICE_URL}/script`);
  const data: Script[] = await response.json();
  return data;
}
