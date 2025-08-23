import React from "react";

import ProjectDashboardClient from "@/app/components/project/ProjectDashboardClient";
import { getCurrentProject } from "@/app/actions/project";
import { getChapters } from "@/app/actions/chapter";
import { redirect } from "next/navigation";
import { getJobState } from "@/app/actions/job";
import { getVoices } from "@/app/actions/voices";
import { getScript } from "@/app/actions/script";
import { getNarration } from "@/app/actions/narrate";

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

  const jobStatePromise = getJobState();
  const voicesPromise = getVoices();
  const scriptPromise = getScript(currentChapter);
  const narrationPromise = getNarration(currentChapter);

  return (
    <ProjectDashboardClient
      project={project}
      chapters={chapters}
      jobStatePromise={jobStatePromise}
      voicesPromise={voicesPromise}
      scriptPromise={scriptPromise}
      narrationPromise={narrationPromise}
    />
  );
}
