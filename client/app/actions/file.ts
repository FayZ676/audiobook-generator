"use server";

import { auth } from "@clerk/nextjs/server";

export async function uploadTextFile(file: File) {
  if (!file) {
    throw new Error("File is required");
  }

  const { userId } = await auth();
  if (!userId) {
    throw new Error("User not authenticated");
  }

  try {
    const fileFormData = new FormData();
    fileFormData.append("file", file);
    const response = await fetch(
      `${process.env.AUDIOBOOK_SERVICE_URL}/text?user_id=${userId}`,
      {
        method: "POST",
        body: fileFormData,
      }
    );
    return response.json();
  } catch (error) {
    console.error("Error uploading file:", error);
    throw error;
  }
}

export async function deleteTextFile(filename: string) {
  const { userId } = await auth();
  if (!userId) {
    throw new Error("User not authenticated");
  }

  try {
    await fetch(
      `${process.env.AUDIOBOOK_SERVICE_URL}/text/${filename}?user_id=${userId}`,
      {
        method: "DELETE",
      }
    );
  } catch (error) {
    console.error("Error deleting file:", error);
    throw error;
  }
}
