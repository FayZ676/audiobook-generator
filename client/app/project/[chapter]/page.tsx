import React from "react";

import { currentUser } from "@clerk/nextjs/server";

import ProjectDashboardClient from "@/app/components/project/ProjectDashboardClient";
import { redirect } from "next/navigation";
import { getDashboardData } from "@/app/actions/dashboard";

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
  const user = await currentUser();
  if (!user) {
    // TODO: Redirect to signin page.
    redirect("/");
  } else {
    const { chapter } = await params;
    const currentChapter = decodeURIComponent(chapter);
    
    const dashboardData = await getDashboardData(currentChapter);
    
    if (!dashboardData.chapters.includes(currentChapter)) {
      redirect("/project");
    }

    return (
      <ProjectDashboardClient
        userId={user.id}
        projectName={dashboardData.projectName}
        chapters={dashboardData.chapters}
        jobStatePromise={Promise.resolve(dashboardData.jobState)}
        voicesPromise={Promise.resolve(dashboardData.voices)}
        scriptPromise={Promise.resolve(dashboardData.script || null)}
        narrationPromise={Promise.resolve(dashboardData.narration || null)}
      />
    );
  }
}
