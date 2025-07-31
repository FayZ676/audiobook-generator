import React from "react";

import ChapterProjectManager from "../chapter/ChapterProjectManager";

interface ProjectDashboardProps {
  currentChapter?: string;
}

export default function ProjectDashboard({
  currentChapter,
}: ProjectDashboardProps) {
  return <ChapterProjectManager currentChapter={currentChapter} />;
}
