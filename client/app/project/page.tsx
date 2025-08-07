import React from "react";
import { redirect } from "next/navigation";

import { getChapters } from "../actions/chapter";
import { getCurrentProject } from "../actions/project";
import ChapterProjectManager from "@/app/components/chapter/ChapterProjectManager";

// Force dynamic rendering since this page uses authentication
export const dynamic = "force-dynamic";

export default async function ProjectHome() {
  if (await getCurrentProject()) {
    const chapters = await getChapters();
    if (chapters.length > 0) {
      redirect(`/project/${encodeURIComponent(chapters[0])}`);
    }
  }

  return <ChapterProjectManager />;
}
