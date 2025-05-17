"use server";

import { auth } from "@clerk/nextjs/server";

export async function uploadTextFile(file: File) {
  const { userId } = await auth();
  if (!userId) {
    throw new Error("User not authenticated");
  }

  try {
    const fileFormData = new FormData();
    const fileExtension = file.name.split(".").pop();
    const uniqueFilename = `${userId}.${fileExtension}`;
    const fileWithCustomName = new File([file], uniqueFilename, {
      type: file.type,
    });

    fileFormData.append("file", fileWithCustomName);
    fileFormData.append("userId", userId);
    const response = await fetch(`${process.env.AUDIOBOOK_SERVICE_URL}/text`, {
      method: "POST",
      body: fileFormData,
    });
    return response.json();
  } catch (error) {
    console.error("Error uploading file:", error);
    throw error;
  }
}

export async function deleteTextFile(filename: string) {
  try {
    await fetch(`${process.env.AUDIOBOOK_SERVICE_URL}/text/${filename}`, {
      method: "DELETE",
    });
  } catch (error) {
    console.error("Error deleting file:", error);
    throw error;
  }
}
