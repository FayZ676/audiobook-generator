"use server";

import { auth } from "@clerk/nextjs/server";

import { deleteTextFile } from "./file";
import { createNarration, deleteNarration } from "./narrate";
import { createScript, deleteScript } from "./script";
import { uploadTextFile } from "./file";

export async function createProject(formData: FormData) {
  const file = formData.get("file") as File;
  const narrator = formData.get("narrator") as string;

  const { userId } = await auth();
  if (!userId) {
    throw new Error("User not authenticated");
  }

  const filename = await uploadTextFile(file);
  await createScript(filename, narrator);
  await createNarration();
}

export async function deleteProject() {
  const { userId } = await auth();
  if (!userId) {
    throw new Error("User not authenticated");
  }
  await deleteTextFile(`${userId}.txt`);
  await deleteNarration(`${userId}.mp3`);
  await deleteScript(`${userId}.json`);
}
