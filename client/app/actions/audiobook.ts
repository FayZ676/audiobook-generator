"use server";

import { auth } from "@clerk/nextjs/server";

import { deleteTextFile } from "./file";
import { deleteNarration } from "./narrate";
import { deleteScript } from "./script";

export async function deleteProject() {
  const { userId } = await auth();
  if (!userId) {
    throw new Error("User not authenticated");
  }
  await deleteTextFile(`${userId}.txt`);
  await deleteNarration(`${userId}.mp3`);
  await deleteScript(`${userId}.json`);
}
