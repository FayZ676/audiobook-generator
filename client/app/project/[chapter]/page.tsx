import React from "react";
import { redirect } from "next/navigation";

import { getChapters } from "../../actions/chapter";
import ProjectDashboard from "@/app/components/project/ProjectDashboard";
import TabSection from "@/app/components/ui/TabSection";

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

  // Validate that the chapter exists
  const chapters = await getChapters();
  if (!chapters.includes(currentChapter)) {
    redirect("/project");
  }

  return (
    <div className="flex flex-col gap-4">
      <TabSection />
      <ProjectDashboard currentChapter={currentChapter} />
    </div>
  );
}
