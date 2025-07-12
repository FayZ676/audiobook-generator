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
    <ul className="menu menu-horizontal bg-base-200 rounded-box">
      {showEditToggle && onToggleEdit && (
        <li>
          <a
            onClick={onToggleEdit}
            className="cursor-pointer font-medium"
            title={isEditing ? "Switch to View Mode" : "Switch to Edit Mode"}
          >
            {isEditing ? "View Mode" : "Edit Mode"}
          </a>
        </li>
      )}
      <li>
        <a
          onClick={onCreateNarration}
          className={`${
            isProcessing || creatingNarration
              ? "disabled cursor-not-allowed opacity-50"
              : "cursor-pointer"
          } font-medium`}
          title={
            isCurrentlyNarrating
              ? "Creating Narration..."
              : creatingNarration
              ? "Creating Narration..."
              : "Create Narration"
          }
        >
          <MicVocal className="h-5 w-5" />
        </a>
      </li>
      <li>
        <a
          onClick={onDeleteScript}
          className={`${
            isProcessing
              ? "disabled cursor-not-allowed opacity-50"
              : "cursor-pointer text-error"
          } font-medium`}
          title="Delete script"
        >
          <Trash2 className="h-5 w-5" />
        </a>
      </li>
    </ul>
  );
}
