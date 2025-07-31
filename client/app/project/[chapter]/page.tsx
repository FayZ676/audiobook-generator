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
  // We're now always showing the first chapter, so we don't need to use the params
  await params; // Still await to satisfy Next.js requirements

  return (
    <div className="flex flex-col gap-4">
      <TabSection />
      <ProjectDashboard />
    </div>
  );
}
