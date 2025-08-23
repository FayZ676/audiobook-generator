import React from "react";
import { redirect } from "next/navigation";

import ProjectDashboardClient from "@/app/components/project/ProjectDashboardClient";
import { getCurrentProject } from "@/app/actions/project";
import { getChapters } from "@/app/actions/chapter";
import { getJobState } from "@/app/actions/job";
import { getVoices } from "@/app/actions/voices";

export const dynamic = "force-dynamic";

export default async function ProjectHome() {
  const project = await getCurrentProject();
  const chapters = await getChapters();

  if (project && chapters.length > 0) {
    redirect(`/project/${encodeURIComponent(chapters[0])}`);
  }

  const jobStatePromise = getJobState();
  const voicesPromise = getVoices();

  return (
    <ProjectDashboardClient
      project={project}
      chapters={chapters}
      jobStatePromise={jobStatePromise}
      voicesPromise={voicesPromise}
      scriptPromise={null}
      narrationPromise={null}
    />
  );
}
