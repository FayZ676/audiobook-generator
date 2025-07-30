import React from "react";
import { redirect } from "next/navigation";

import { getChapters } from "../actions/chapter";
import { getCurrentProject } from "../actions/project";
import ProjectDashboard from "@/app/components/project/ProjectDashboard";
import TabSection from "@/app/components/ui/TabSection";

// Force dynamic rendering since this page uses authentication
export const dynamic = "force-dynamic";

export default async function ProjectHome() {
  const project = await getCurrentProject();

  if (project) {
    const chapters = await getChapters();

    // If there are chapters, redirect to the first one
    if (chapters.length > 0) {
      redirect(`/project/${encodeURIComponent(chapters[0])}`);
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <TabSection />
      <ProjectDashboard />
    </div>
  );
}
