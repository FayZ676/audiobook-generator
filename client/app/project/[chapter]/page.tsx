import React from "react";

import ProjectDashboard from "@/app/components/project/ProjectDashboard";
import { getChapters } from "@/app/actions/chapter";
import { redirect } from "next/navigation";

// Force dynamic rendering since this page uses authentication
export const dynamic = "force-dynamic";

interface ProjectChapterPageProps {
  params: Promise<{
    chapter: string;
  }>;
}

export default async function ProjectChapterPage({
  params,
}: ProjectChapterPageProps) {
  const { chapter } = await params;
  const currentChapter = decodeURIComponent(chapter);
  const chapters = await getChapters();

  if (!chapters.includes(currentChapter)) {
    redirect("/project");
  }

  return (
    <ProjectDashboard
      currentChapter={currentChapter}
      initialChapters={chapters}
    />
  );
}
