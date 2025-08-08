"use client";

import React from "react";

interface ChapterSelectorProps {
  chapters: string[];
  onChapterSelect: (chapter: string) => void;
}

export default function ChapterSelector({
  chapters,
  onChapterSelect,
}: ChapterSelectorProps) {
  if (chapters.length === 0) {
    return (
      <div className="text-center py-4">
        No chapters yet. Create your first chapter to get started.
      </div>
    );
  }

  return (
    <div className="space-y-2 w-full">
      <div className="space-y-1">
        {chapters.map((chapter) => (
          <button
            key={chapter}
            className="btn btn-block"
            onClick={() => onChapterSelect(chapter)}
          >
            <h6 className="truncate">{chapter}</h6>
          </button>
        ))}
      </div>
    </div>
  );
}
