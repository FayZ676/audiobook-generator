"use server";

import { revalidateTag } from "next/cache";
import { getUserId } from "./user";
import { apiCallVoid, apiCallJson } from "../lib/api";

interface CreateProjectRequest {
  user_id: string;
  project_name: string;
}

interface CreateProjectProps {
  projectName: string;
}

export async function createProject({ projectName }: CreateProjectProps) {
  const userId = await getUserId();

  const request: CreateProjectRequest = {
    user_id: userId,
    project_name: projectName,
  };

  try {
    await apiCallVoid(`${process.env.AUDIOBOOK_SERVICE_URL}/project`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
    });

    revalidateTag("project");
  } catch (error) {
    console.error("Error creating project:", error);
    throw error;
  }
}

export async function deleteProject() {
  const userId = await getUserId();

  await apiCallVoid(`${process.env.AUDIOBOOK_SERVICE_URL}/project/${userId}`, {
    method: "DELETE",
    headers: {
      "Content-Type": "application/json",
    },
  });

  revalidateTag("project");
}

export async function getCurrentProject(): Promise<{
  name: string;
  created_at: string;
} | null> {
  const userId = await getUserId();

  try {
    const project = await apiCallJson<{
      name: string;
      created_at: string;
    } | null>(`${process.env.AUDIOBOOK_SERVICE_URL}/project/${userId}`, {
      cache: "force-cache",
      next: {
        tags: ["project"],
      },
    });
    return project;
  } catch (error) {
    console.error("Error fetching current project:", error);
    return null;
  }
}
