import React from "react";

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
  const resolvedParams = await params;

  return (
    <div className="flex flex-col gap-4">
      <TabSection />
      <ProjectDashboard
        selectedChapter={decodeURIComponent(resolvedParams.chapter)}
      />
    </div>
  );
}
