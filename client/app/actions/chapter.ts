"use server";

import { revalidateTag } from "next/cache";
import { getUserId } from "./user";
import { apiCallVoid, apiCallJson } from "../lib/api";

interface CreateChapterRequest {
  user_id: string;
  chapter_name: string;
}

interface CreateChapterProps {
  chapterName: string;
}

export async function createChapter({ chapterName }: CreateChapterProps) {
  const userId = await getUserId();

  const request: CreateChapterRequest = {
    user_id: userId,
    chapter_name: chapterName,
  };

  try {
    await apiCallVoid(`${process.env.AUDIOBOOK_SERVICE_URL}/chapter`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
    });

    revalidateTag("chapters");
    revalidateTag("project");
  } catch (error) {
    console.error("Error creating chapter:", error);
    throw error;
  }
}

export async function getChapters(): Promise<string[]> {
  const userId = await getUserId();

  try {
    const chapters = await apiCallJson<string[]>(
      `${process.env.AUDIOBOOK_SERVICE_URL}/chapters/${userId}`,
      {
        cache: "force-cache",
        next: {
          tags: ["chapters"],
        },
      }
    );

    return chapters || [];
  } catch (error) {
    console.error("Error fetching chapters:", error);
    return [];
  }
}

export async function deleteChapter(chapterId: string) {
  const userId = await getUserId();

  await apiCallVoid(
    `${process.env.AUDIOBOOK_SERVICE_URL}/chapter/${userId}/${chapterId}`,
    {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
      },
    }
  );

  revalidateTag("chapters");
  revalidateTag("project");
}
