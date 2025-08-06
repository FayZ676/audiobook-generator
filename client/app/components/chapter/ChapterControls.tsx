"use client";

import React, { useState } from "react";
import { use } from "react";
import { MicVocal, Trash2 } from "lucide-react";

import { createNarration } from "../../actions/narrate";
import { Script } from "../../actions/script";
import { AudiobookJob } from "../../actions/job";
import { Voice } from "../../actions/voices";
import { deleteChapter } from "../../actions/chapter";
import Tip from "../ui/Tip";

interface ChapterControlsProps {
  narrationUrlPromise: Promise<string | null>;
  scriptPromise: Promise<Script | null>;
  jobStatePromise: Promise<AudiobookJob | null>;
  voicesPromise: Promise<Voice[]>;
  isEditing: boolean;
  onEditToggle: (editing: boolean) => void;
  chapterName: string;
  onChapterDeleted?: () => void;
}

export default function ChapterControls({
  narrationUrlPromise,
  scriptPromise,
  jobStatePromise,
  voicesPromise,
  isEditing,
  onEditToggle,
  chapterName,
  onChapterDeleted,
}: ChapterControlsProps) {
  const [isCreatingNarration, setIsCreatingNarration] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const narrationUrl = use(narrationUrlPromise);
  const script = use(scriptPromise);
  const jobState = use(jobStatePromise);
  const voices = use(voicesPromise);

  const handleCreateNarration = async (e: React.MouseEvent) => {
    e.preventDefault();
    setIsCreatingNarration(true);
    setError(null);
    try {
      await createNarration(chapterName);
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : String(error);
      setError(errorMessage ? errorMessage : "Something went wrong.");
    } finally {
      setIsCreatingNarration(false);
    }
  };

  const handleDeleteChapter = async () => {
    try {
      await deleteChapter(chapterName);
      onChapterDeleted?.();
    } catch (error) {
      console.error("Error deleting chapter:", error);
      setError("Failed to delete chapter");
    }
  };

  const isProcessing =
    jobState?.script_status === "processing" ||
    jobState?.narration_status === "processing";

  return (
    <div className="flex items-center justify-between gap-4">
      {error && <Tip variant="warning">{error}</Tip>}

      {script && (
        <label className="flex cursor-pointer gap-2">
          <span className="label-text">View</span>
          <input
            type="checkbox"
            checked={isEditing}
            onChange={(e) => onEditToggle(e.target.checked)}
            disabled={isProcessing || voices.length === 0}
            className="toggle"
          />
          <span className="label-text">Edit</span>
        </label>
      )}

      <div className="flex gap-2">
        {script && (
          <button
            className={`btn btn-sm ${
              isCreatingNarration || isProcessing
                ? "btn-disabled"
                : "btn-primary"
            }`}
            onClick={
              isCreatingNarration || isProcessing
                ? undefined
                : (e) => {
                    setError(null);
                    handleCreateNarration(e);
                  }
            }
            title={
              isCreatingNarration || jobState?.narration_status === "processing"
                ? "Creating Narration..."
                : narrationUrl
                ? "Regenerate Narration"
                : "Narrate"
            }
          >
            <MicVocal className="h-4 w-4" />
          </button>
        )}

        <button
          className="btn btn-sm btn-error"
          onClick={handleDeleteChapter}
          title="Delete chapter"
        >
          <Trash2 className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}
