"use client";

import React from "react";
import { MicVocal, Trash2 } from "lucide-react";
import { AudiobookJob } from "../../actions/job";

interface ScriptControlsProps {
  filename: string;
  jobState: AudiobookJob | null;
  creatingNarration: boolean;
  isEditing?: boolean;
  showEditToggle?: boolean;
  onCreateNarration: (event: React.MouseEvent) => void;
  onDeleteScript: (event: React.MouseEvent) => void;
  onToggleEdit?: () => void;
}

export default function ScriptControls({
  filename,
  jobState,
  creatingNarration,
  isEditing,
  showEditToggle = false,
  onCreateNarration,
  onDeleteScript,
  onToggleEdit,
}: ScriptControlsProps) {
  const isProcessing =
    jobState?.script_status === "processing" ||
    jobState?.narration_status === "processing";
  const isCurrentlyNarrating =
    jobState?.current_script_filename === filename &&
    jobState?.narration_status === "processing";

  return (
    <div className="flex gap-2">
      {showEditToggle && onToggleEdit && (
        <button onClick={onToggleEdit} className="btn btn-sm">
          {isEditing ? "View Mode" : "Edit Mode"}
        </button>
      )}
      <button
        onClick={onCreateNarration}
        className={`btn btn-ghost btn-sm ${
          isProcessing || creatingNarration
            ? "loading cursor-not-allowed opacity-50"
            : "hover:bg-primary hover:text-primary-content"
        }`}
        disabled={isProcessing || creatingNarration}
        title={
          isCurrentlyNarrating
            ? "Creating Narration..."
            : creatingNarration
            ? "Creating Narration..."
            : "Create Narration"
        }
      >
        <MicVocal className="h-4 w-4" />
      </button>
      <button
        onClick={onDeleteScript}
        className={`btn btn-ghost btn-sm ${
          isProcessing
            ? "cursor-not-allowed opacity-50"
            : "text-error hover:bg-error hover:text-error-content"
        }`}
        disabled={isProcessing}
        title="Delete script"
      >
        <Trash2 className="h-4 w-4" />
      </button>
    </div>
  );
}
