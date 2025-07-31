import React from "react";

import ChapterProjectManager from "../chapter/ChapterProjectManager";

interface ProjectDashboardProps {
  currentChapter?: string;
}

export default function ProjectDashboard({
  currentChapter,
}: ProjectDashboardProps) {
  return (
    <div className="flex flex-col gap-4">
      <ChapterProjectManager currentChapter={currentChapter} />
    </div>
  );
}
