import React from "react";

import { redirect } from "next/navigation";

import { currentUser } from "@clerk/nextjs/server";

import ProjectDashboardClient from "@/app/components/project/ProjectDashboardClient";
import { getCurrentProjectName } from "@/app/actions/project";
import { getChapters } from "@/app/actions/chapter";
import { getJobState } from "@/app/actions/job";
import { getVoices } from "@/app/actions/voices";

export const dynamic = "force-dynamic";

export default async function ProjectHome() {
  const user = await currentUser();
  if (!user) {
    // TODO: Redirect to signin page.
    redirect("/");
  } else {
    const project = await getCurrentProjectName();
    const chapters = await getChapters();
    if (project && chapters.length > 0) {
      redirect(`/project/${encodeURIComponent(chapters[0])}`);
    }
    const jobStatePromise = getJobState();
    const voicesPromise = getVoices();

    return (
      <ProjectDashboardClient
        userId={user.id}
        projectName={project}
        chapters={chapters}
        jobStatePromise={jobStatePromise}
        voicesPromise={voicesPromise}
        scriptPromise={null}
        narrationPromise={null}
      />
    );
  }
}
