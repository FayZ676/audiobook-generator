"use client";

import React, { useState } from "react";
import { use } from "react";
import { FileText, Edit3, MicVocal, Trash2 } from "lucide-react";

import { createNarration } from "../../actions/narrate";
import { Script } from "../../actions/script";
import { AudiobookJob } from "../../actions/job";
import { Voice } from "../../actions/voices";
import { deleteChapter } from "../../actions/chapter";
import Tip from "../ui/Tip";

interface ScriptControlsProps {
  narrationUrlPromise: Promise<string | null>;
  scriptPromise: Promise<Script | null>;
  jobStatePromise: Promise<AudiobookJob | null>;
  voicesPromise: Promise<Voice[]>;
  isEditing: boolean;
  onEditToggle: (editing: boolean) => void;
  chapterName: string;
  onChapterDeleted?: () => void;
}

export default function ScriptControls({
  narrationUrlPromise,
  scriptPromise,
  jobStatePromise,
  voicesPromise,
  isEditing,
  onEditToggle,
  chapterName,
  onChapterDeleted,
}: ScriptControlsProps) {
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
      setError("Failed to delete chapter");
    }
  };

  const isProcessing =
    jobState?.script_status === "processing" ||
    jobState?.narration_status === "processing";

  return (
    <div className="flex flex-col gap-2">
      {error && <Tip variant="warning">{error}</Tip>}
      <div className="flex justify-between items-center">
        <h3 className="font-bold">Script controls</h3>
        <ul className="menu menu-horizontal bg-base-200 rounded-box">
          {script && (
            <>
              <li>
                <a
                  className={!isEditing ? "active" : ""}
                  onClick={() => onEditToggle(false)}
                  title="View script"
                >
                  <FileText className="h-5 w-5" />
                </a>
              </li>
              <li>
                <a
                  className={`${isEditing ? "active" : ""} ${
                    isProcessing || voices.length === 0
                      ? "disabled cursor-not-allowed opacity-50"
                      : "cursor-pointer"
                  }`}
                  onClick={
                    isProcessing || voices.length === 0
                      ? undefined
                      : () => onEditToggle(true)
                  }
                  title="Edit script"
                >
                  <Edit3 className="h-5 w-5" />
                </a>
              </li>
            </>
          )}
          {script && (
            <li>
              <a
                className={`${
                  isCreatingNarration || isProcessing
                    ? "disabled cursor-not-allowed opacity-50"
                    : "cursor-pointer"
                } font-medium`}
                onClick={
                  isCreatingNarration || isProcessing
                    ? undefined
                    : (e) => {
                        setError(null);
                        handleCreateNarration(e);
                      }
                }
                title={
                  isCreatingNarration ||
                  jobState?.narration_status === "processing"
                    ? "Creating Narration..."
                    : narrationUrl
                    ? "Regenerate Narration"
                    : "Narrate"
                }
              >
                <MicVocal className="h-5 w-5" />
              </a>
            </li>
          )}
          <li>
            <a
              className="cursor-pointer text-error hover:bg-error/10"
              onClick={handleDeleteChapter}
              title="Delete chapter"
            >
              <Trash2 className="h-5 w-5" />
            </a>
          </li>
        </ul>
      </div>
    </div>
  );
}
