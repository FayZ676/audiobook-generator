"use client";

import React, { useState } from "react";
import { use } from "react";
import { useRouter } from "next/navigation";
import { FileText, Edit3, MicVocal, Trash2, Plus } from "lucide-react";

import { createNarration } from "../../actions/narrate";
import { deleteProject } from "../../actions/audiobook";
import { Script } from "../../actions/script";
import { AudiobookJob } from "../../actions/job";
import { Voice } from "../../actions/voices";
import GenerateScriptModal from "./GenerateScriptModal";

interface ScriptControlsProps {
  narrationUrlPromise: Promise<string | null>;
  scriptPromise: Promise<Script | null>;
  jobStatePromise: Promise<AudiobookJob | null>;
  voicesPromise: Promise<Voice[]>;
  isEditing: boolean;
  onEditToggle: (editing: boolean) => void;
}

export default function ScriptControls({
  narrationUrlPromise,
  scriptPromise,
  jobStatePromise,
  voicesPromise,
  isEditing,
  onEditToggle,
}: ScriptControlsProps) {
  const router = useRouter();
  const [isCreatingNarration, setIsCreatingNarration] = useState(false);
  const [isDeletingProject, setIsDeletingProject] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const narrationUrl = use(narrationUrlPromise);
  const script = use(scriptPromise);
  const jobState = use(jobStatePromise);
  const voices = use(voicesPromise);

  const handleCreateNarration = async (e: React.MouseEvent) => {
    e.preventDefault();
    setIsCreatingNarration(true);
    try {
      await createNarration();
    } catch (error) {
      console.error("Error creating narration:", error);
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
      console.error("Error deleting project:", error);
    } finally {
      setIsDeletingProject(false);
    }
  };

  const isProcessing =
    jobState?.script_status === "processing" ||
    jobState?.narration_status === "processing";

  return (
    <>
      <div className="flex justify-between items-center">
        <h3 className="font-bold">Script controls</h3>
        <ul className="menu menu-horizontal bg-base-200 rounded-box">
          <li>
            <a
              className={`${
                isProcessing || isDeletingProject
                  ? "disabled cursor-not-allowed opacity-50"
                  : "cursor-pointer"
              } font-medium`}
              onClick={
                isProcessing || isDeletingProject
                  ? undefined
                  : () => setIsModalOpen(true)
              }
              title="Add New Chapter"
            >
              <Plus className="h-5 w-5" />
            </a>
          </li>
          <li>
            <a
              className={`${!isEditing ? "active" : ""} ${
                !script
                  ? "disabled cursor-not-allowed opacity-50"
                  : "cursor-pointer"
              }`}
              onClick={script ? () => onEditToggle(false) : undefined}
              title="View script"
            >
              <FileText className="h-5 w-5" />
            </a>
          </li>
          <li>
            <a
              className={`${isEditing ? "active" : ""} ${
                !script ||
                isProcessing ||
                isDeletingProject ||
                voices.length === 0
                  ? "disabled cursor-not-allowed opacity-50"
                  : "cursor-pointer"
              }`}
              onClick={
                !script ||
                isProcessing ||
                isDeletingProject ||
                voices.length === 0
                  ? undefined
                  : () => onEditToggle(true)
              }
              title="Edit script"
            >
              <Edit3 className="h-5 w-5" />
            </a>
          </li>
          <li>
            <a
              className={`${
                !script ||
                isCreatingNarration ||
                isProcessing ||
                isDeletingProject
                  ? "disabled cursor-not-allowed opacity-50"
                  : "cursor-pointer"
              } font-medium`}
              onClick={
                !script ||
                isCreatingNarration ||
                isProcessing ||
                isDeletingProject
                  ? undefined
                  : handleCreateNarration
              }
              title={
                !script
                  ? "No script available"
                  : isCreatingNarration ||
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
          <li>
            <a
              className={`${
                (!script && !narrationUrl) || isDeletingProject || isProcessing
                  ? "disabled cursor-not-allowed opacity-50"
                  : "cursor-pointer"
              } font-medium`}
              onClick={
                (!script && !narrationUrl) || isDeletingProject || isProcessing
                  ? undefined
                  : handleDeleteProject
              }
              title={
                !script && !narrationUrl
                  ? "Nothing to delete"
                  : isDeletingProject
                  ? "Deleting Project..."
                  : "Delete Project"
              }
            >
              <Trash2 className="h-5 w-5" />
            </a>
          </li>
        </ul>
      </div>
      <GenerateScriptModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        existingScript={script}
      />
    </>
  );
}
