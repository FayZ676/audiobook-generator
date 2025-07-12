"use client";

import React, { useState } from "react";
import { MicVocal, Trash2 } from "lucide-react";
import { Script, getUserScript, deleteScript } from "../../actions/script";
import { createNarration } from "../../actions/narrate";
import { Voice } from "../../actions/voices";
import { AudiobookJob } from "../../actions/job";
import ScriptText from "./ScriptText";

interface ScriptInfo {
  filename: string;
  s3_key: string;
}

interface ScriptItemProps {
  scriptInfo: ScriptInfo;
  voices: Voice[];
  jobState: AudiobookJob | null;
  isSelected: boolean;
  onRefresh: () => void;
}

export default function ScriptItem({
  scriptInfo,
  voices,
  jobState,
  isSelected,
  onRefresh,
}: ScriptItemProps) {
  const [selectedScript, setSelectedScript] = useState<Script | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [loadingScript, setLoadingScript] = useState(false);
  const [creatingNarration, setCreatingNarration] = useState(false);

  React.useEffect(() => {
    if (isSelected && !selectedScript) {
      const loadScript = async () => {
        setLoadingScript(true);
        try {
          const script = await getUserScript(scriptInfo.filename);
          setSelectedScript(script);
        } catch (error) {
          console.error("Error loading script:", error);
        } finally {
          setLoadingScript(false);
        }
      };
      loadScript();
    } else if (!isSelected) {
      setSelectedScript(null);
      setIsEditing(false);
    }
  }, [isSelected, scriptInfo.filename, selectedScript]);

  const handleDeleteScript = async (event: React.MouseEvent) => {
    event.stopPropagation();

    if (confirm(`Are you sure you want to delete "${scriptInfo.filename}"?`)) {
      try {
        await deleteScript(scriptInfo.filename);
        onRefresh();
      } catch (error) {
        console.error("Error deleting script:", error);
      }
    }
  };

  const handleCreateNarration = async (event: React.MouseEvent) => {
    event.stopPropagation();

    setCreatingNarration(true);
    try {
      await createNarration(scriptInfo.filename);
    } catch (error) {
      console.error("Error creating narration:", error);
    } finally {
      setCreatingNarration(false);
    }
  };

  const isProcessing =
    jobState?.script_status === "processing" ||
    jobState?.narration_status === "processing";
  const isCurrentlyNarrating =
    jobState?.current_script_filename === scriptInfo.filename &&
    jobState?.narration_status === "processing";

  return (
    <>
      <div className="collapse-title text-xl font-medium flex justify-between items-center">
        <span>{scriptInfo.filename}</span>
        <div className="flex gap-2">
          <button
            onClick={handleCreateNarration}
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
            onClick={handleDeleteScript}
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
      </div>
      <div className="collapse-content">
        {loadingScript ? (
          <div className="flex justify-center py-4">
            <span className="loading loading-spinner loading-md"></span>
          </div>
        ) : selectedScript && isSelected ? (
          <div className="space-y-4">
            <div className="flex justify-end">
              <button
                onClick={() => setIsEditing(!isEditing)}
                className="btn btn-sm"
              >
                {isEditing ? "View Mode" : "Edit Mode"}
              </button>
            </div>
            <ScriptText
              script={selectedScript}
              voices={voices}
              isEditing={isEditing}
              filename={scriptInfo.filename}
            />
          </div>
        ) : null}
      </div>
    </>
  );
}
