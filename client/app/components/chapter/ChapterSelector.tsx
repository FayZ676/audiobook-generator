"use client";

import React, { useState } from "react";
import { Trash2, LoaderCircle } from "lucide-react";

import { deleteChapter } from "../../actions/chapter";

interface ChapterSelectorProps {
  chapters: string[];
  onChapterSelect: (chapter: string) => void;
  onChapterDeleted?: () => void;
}

export default function ChapterSelector({
  chapters,
  onChapterSelect,
  onChapterDeleted,
}: ChapterSelectorProps) {
  const [deletingChapter, setDeletingChapter] = useState<string | null>(null);

  if (chapters.length === 0) {
    return (
      <div className="text-center py-4">
        No chapters yet. Create your first chapter to get started.
      </div>
    );
  }

  const handleDelete = async (chapter: string) => {
    if (deletingChapter) return;
    setDeletingChapter(chapter);
    try {
      await deleteChapter(chapter);
      onChapterDeleted?.();
    } catch (error) {
      console.error("Failed to delete chapter:", error);
      alert("Failed to delete chapter. Please try again.");
    } finally {
      setDeletingChapter(null);
    }
  };

  return (
    <div className="space-y-2 w-full">
      <div className="space-y-1">
        {chapters.map((chapter) => (
          <div key={chapter} className="flex items-center gap-2 w-full">
            <button
              className="btn flex-1"
              onClick={() => onChapterSelect(chapter)}
            >
              <h6 className="truncate">{chapter}</h6>
            </button>
            <button
              onClick={() => handleDelete(chapter)}
              disabled={deletingChapter === chapter}
              className={`btn btn-sm btn-outline ${
                deletingChapter === chapter ? "btn-disabled" : "btn-error"
              }`}
              title="Delete chapter"
            >
              {deletingChapter === chapter ? (
                <LoaderCircle size={16} className="animate-spin" />
              ) : (
                <Trash2 size={16} />
              )}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
