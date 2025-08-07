import React from "react";

import ProjectDashboard from "@/app/components/chapter/ProjectDashboard";

// Force dynamic rendering since this page uses authentication
export const dynamic = "force-dynamic";

export default async function ProjectHome() {
  return <ProjectDashboard />;
}
