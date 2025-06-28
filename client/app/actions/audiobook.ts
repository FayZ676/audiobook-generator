"use server";

import { revalidateTag } from "next/cache";

import { auth } from "@clerk/nextjs/server";

import { deleteNarration } from "./narrate";
import { deleteScript } from "./script";
import { deleteJob } from "./job";

export async function deleteProject() {
  const { userId } = await auth();
  if (!userId) {
    throw new Error("User not authenticated");
  }
  await deleteNarration(`${userId}.mp3`);
  await deleteScript(`${userId}.json`);
  await deleteJob(`${userId}.json`);

  revalidateTag("script");
  revalidateTag("narration");
  revalidateTag("job");
}
