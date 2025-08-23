import React from "react";

import ProjectDashboardClient from "@/app/components/project/ProjectDashboardClient";

// Force dynamic rendering since this page uses authentication
export const dynamic = "force-dynamic";

export default async function ProjectHome() {
  return <ProjectDashboardClient />;
}
