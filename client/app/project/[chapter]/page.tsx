import React from "react";

import ProjectDashboardClient from "@/app/components/project/ProjectDashboardClient";
import { getCurrentProject } from "@/app/actions/project";
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

  const project = await getCurrentProject();
  const chapters = await getChapters();

  if (!chapters.includes(currentChapter)) {
    redirect("/project");
  }

  return <ProjectDashboardClient project={project} chapters={chapters} />;
}
