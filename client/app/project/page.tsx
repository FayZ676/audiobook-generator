import React from "react";

import ChapterProjectManager from "@/app/components/chapter/ChapterProjectManager";

// Force dynamic rendering since this page uses authentication
export const dynamic = "force-dynamic";

export default async function ProjectHome() {
  return <ChapterProjectManager />;
}
