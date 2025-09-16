import React from "react";

import { redirect } from "next/navigation";

import { currentUser } from "@clerk/nextjs/server";

import ProjectDashboardClient from "@/app/components/project/ProjectDashboardClient";
import { getDashboardData } from "@/app/actions/dashboard";

export const dynamic = "force-dynamic";

export default async function ProjectHome() {
  const user = await currentUser();
  if (!user) {
    // TODO: Redirect to signin page.
    redirect("/");
  } else {
    const dashboardData = await getDashboardData();
    
    if (dashboardData.projectName && dashboardData.chapters.length > 0) {
      redirect(`/project/${encodeURIComponent(dashboardData.chapters[0])}`);
    }

    return (
      <ProjectDashboardClient
        userId={user.id}
        projectName={dashboardData.projectName}
        chapters={dashboardData.chapters}
        jobStatePromise={Promise.resolve(dashboardData.jobState)}
        voicesPromise={Promise.resolve(dashboardData.voices)}
        scriptPromise={null}
        narrationPromise={null}
      />
    );
  }
}
