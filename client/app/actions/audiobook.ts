"use server";

import { revalidateTag } from "next/cache";

import { auth } from "@clerk/nextjs/server";

import { deleteJob } from "./job";
import { deleteProject as deleteUserProject } from "./project";

export async function deleteProject() {
  const { userId } = await auth();
  if (!userId) {
    throw new Error("User not authenticated");
  }

  await deleteJob(`${userId}.json`);
  await deleteUserProject();

  revalidateTag("script");
  revalidateTag("narration");
  revalidateTag("job");
  revalidateTag("project");
  revalidateTag("chapters");
}
