import React from "react";
import { redirect } from "next/navigation";

import ProjectDashboardClient from "@/app/components/project/ProjectDashboardClient";
import { getCurrentProject } from "@/app/actions/project";
import { getChapters } from "@/app/actions/chapter";

export const dynamic = "force-dynamic";

export default async function ProjectHome() {
  const project = await getCurrentProject();
  const chapters = await getChapters();

  if (project && chapters.length > 0) {
    redirect(`/project/${encodeURIComponent(chapters[0])}`);
  }

  return <ProjectDashboardClient project={project} chapters={chapters} />;
}
