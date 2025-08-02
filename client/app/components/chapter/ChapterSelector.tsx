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
      <div className="text-center text-base-content/60 py-4">
        No chapters yet. Create your first chapter to get started.
      </div>
    );
  }

  return (
    <div className="space-y-2 w-full">
      <h4 className="">Chapters</h4>
      <div className="space-y-1">
        {chapters.map((chapter) => (
          <button
            key={chapter}
            className="btn btn-ghost btn-block"
            onClick={() => onChapterSelect(chapter)}
          >
            <div className="font-medium truncate">{chapter}</div>
          </button>
        ))}
      </div>
    </div>
  );
}
