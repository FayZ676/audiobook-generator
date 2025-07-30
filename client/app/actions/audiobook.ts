"use server";

import { revalidateTag } from "next/cache";

import { auth } from "@clerk/nextjs/server";

import { deleteNarration } from "./narrate";
import { deleteScript } from "./script";
import { deleteJob } from "./job";
import { deleteProject as deleteUserProject } from "./project";

export async function deleteProject() {
  const { userId } = await auth();
  if (!userId) {
    throw new Error("User not authenticated");
  }
  await deleteNarration(`${userId}.mp3`);
  await deleteScript(`${userId}.json`);
  await deleteJob(`${userId}.json`);
  await deleteUserProject();

  revalidateTag("script");
  revalidateTag("narration");
  revalidateTag("job");
  revalidateTag("project");
}
