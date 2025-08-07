import React from "react";

import ChapterProjectManager from "@/app/components/chapter/ChapterProjectManager";

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

  return <ChapterProjectManager currentChapter={currentChapter} />;
}
