import React from "react";

import ProjectDashboard from "@/app/components/project/ProjectDashboard";
import TabSection from "@/app/components/ui/TabSection";

// Force dynamic rendering since this page uses authentication
export const dynamic = "force-dynamic";

export default function ProjectHome() {
  return (
    <div className="flex flex-col gap-4">
      <TabSection />
      <ProjectDashboard />
    </div>
  );
}
