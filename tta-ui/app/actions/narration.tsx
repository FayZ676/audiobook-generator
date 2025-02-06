"use server";

export async function generate(text: string) {
  const formData = new FormData();
  formData.append(
    "file",
    new Blob([text], { type: "text/plain" }),
    "story.txt"
  );

  const response = await fetch("http://localhost:8000/narration", {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Failed to generate narration");
  }

  const arrayBuffer = await response.arrayBuffer();
  const uint8Array = new Uint8Array(arrayBuffer);
  const base64String = Buffer.from(uint8Array).toString("base64");
  return base64String;
}
