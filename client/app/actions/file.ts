"use server";

export async function uploadTextFile(file: File) {
  if (!file) {
    throw new Error("File is required");
  }

  try {
    const fileFormData = new FormData();
    fileFormData.append("file", file);
    const filename = await fetch(`${process.env.AUDIOBOOK_SERVICE_URL}/text`, {
      method: "POST",
      body: fileFormData,
    });
    return filename;
  } catch (error) {
    console.error("Error uploading file:", error);
    throw error;
  }
}
