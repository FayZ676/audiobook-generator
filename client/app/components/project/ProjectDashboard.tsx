import React from "react";

import ChapterProjectManager from "../chapter/ChapterProjectManager";

interface ProjectDashboardProps {
  selectedChapter?: string;
}

export default function ProjectDashboard({
  selectedChapter,
}: ProjectDashboardProps) {
  return (
    <div className="flex flex-col gap-4">
      <ChapterProjectManager selectedChapter={selectedChapter} />
    </div>
  );
}
