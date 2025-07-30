"use client";

import React from "react";
import { Book, Trash2 } from "lucide-react";

import { deleteChapter } from "../../actions/chapter";

interface ChapterSelectorProps {
  chapters: string[];
  selectedChapter: string | null;
  onChapterSelect: (chapter: string) => void;
  onChapterDeleted?: () => void;
}

export default function ChapterSelector({
  chapters,
  selectedChapter,
  onChapterSelect,
  onChapterDeleted,
}: ChapterSelectorProps) {
  const handleDeleteChapter = async (chapterName: string) => {
    if (
      !confirm(
        `Are you sure you want to delete "${chapterName}"? This will permanently delete all scripts and narrations for this chapter.`
      )
    ) {
      return;
    }

    try {
      await deleteChapter(chapterName);
      onChapterDeleted?.();
    } catch (error) {
      console.error("Error deleting chapter:", error);
      alert("Failed to delete chapter");
    }
  };

  const getStatusIcon = () => {
    return <Book className="h-4 w-4 text-base-content/50" />;
  };

  const getStatusText = () => {
    return "Chapter";
  };

  if (chapters.length === 0) {
    return (
      <div className="text-center text-base-content/60 py-4">
        No chapters yet. Create your first chapter to get started.
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <h4 className="font-semibold text-sm text-base-content/80">Chapters</h4>
      <div className="space-y-1">
        {chapters.map((chapter) => (
          <div
            key={chapter}
            className={`flex items-center justify-between p-3 rounded-lg border cursor-pointer transition-colors ${
              selectedChapter === chapter
                ? "bg-primary/10 border-primary"
                : "bg-base-100 border-base-200 hover:bg-base-200/50"
            }`}
            onClick={() => onChapterSelect(chapter)}
          >
            <div className="flex items-center gap-3 flex-1 min-w-0">
              {getStatusIcon()}
              <div className="flex-1 min-w-0">
                <div className="font-medium truncate">{chapter}</div>
                <div className="text-xs text-base-content/60">
                  {getStatusText()}
                </div>
              </div>
            </div>

            <button
              onClick={(e) => {
                e.stopPropagation();
                handleDeleteChapter(chapter);
              }}
              className="btn btn-ghost btn-xs text-error hover:bg-error/10"
              title="Delete chapter"
            >
              <Trash2 className="h-3 w-3" />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
