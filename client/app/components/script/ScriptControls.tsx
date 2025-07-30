"use client";

import React, { useState } from "react";
import { use } from "react";
import { useRouter } from "next/navigation";
import { FileText, Edit3, MicVocal, Trash2 } from "lucide-react";

import { createNarration } from "../../actions/narrate";
import { deleteProject } from "../../actions/audiobook";
import { Script } from "../../actions/script";
import { AudiobookJob } from "../../actions/job";
import { Voice } from "../../actions/voices";
import Tip from "../ui/Tip";

interface ScriptControlsProps {
  narrationUrlPromise: Promise<string | null>;
  scriptPromise: Promise<Script | null>;
  jobStatePromise: Promise<AudiobookJob | null>;
  voicesPromise: Promise<Voice[]>;
  isEditing: boolean;
  onEditToggle: (editing: boolean) => void;
  chapterName: string;
}

export default function ScriptControls({
  narrationUrlPromise,
  scriptPromise,
  jobStatePromise,
  voicesPromise,
  isEditing,
  onEditToggle,
  chapterName,
}: ScriptControlsProps) {
  const router = useRouter();
  const [isCreatingNarration, setIsCreatingNarration] = useState(false);
  const [isDeletingProject, setIsDeletingProject] = useState(false);
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

  const handleDeleteProject = async (e: React.MouseEvent) => {
    e.preventDefault();
    setIsDeletingProject(true);
    try {
      await deleteProject();
      router.refresh();
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : String(error);
      setError(errorMessage ? errorMessage : "Something went wrong.");
    } finally {
      setIsDeletingProject(false);
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
                    isProcessing || isDeletingProject || voices.length === 0
                      ? "disabled cursor-not-allowed opacity-50"
                      : "cursor-pointer"
                  }`}
                  onClick={
                    isProcessing || isDeletingProject || voices.length === 0
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
                  isCreatingNarration || isProcessing || isDeletingProject
                    ? "disabled cursor-not-allowed opacity-50"
                    : "cursor-pointer"
                } font-medium`}
                onClick={
                  isCreatingNarration || isProcessing || isDeletingProject
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
          {(script || narrationUrl) && (
            <li>
              <a
                className={`${
                  isDeletingProject || isProcessing
                    ? "disabled cursor-not-allowed opacity-50"
                    : "cursor-pointer"
                } font-medium`}
                onClick={
                  isDeletingProject || isProcessing
                    ? undefined
                    : handleDeleteProject
                }
                title={
                  isDeletingProject ? "Deleting Project..." : "Delete Project"
                }
              >
                <Trash2 className="h-5 w-5" />
              </a>
            </li>
          )}
        </ul>
      </div>
    </div>
  );
}
