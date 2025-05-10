"use server";

export async function uploadTextFile(formData: FormData) {
  const file = formData.get("file") as File;

  if (!file) {
    throw new Error("File is required");
  }

  try {
    const fileFormData = new FormData();
    fileFormData.append("file", file);
    await fetch(`${process.env.AUDIOBOOK_SERVICE_URL}/text`, {
      method: "POST",
      body: fileFormData,
    });
  } catch (error) {
    console.error("Error uploading file:", error);
    throw error;
  }
}
