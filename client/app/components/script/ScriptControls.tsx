"use client";

import React, { useState } from "react";
import { use } from "react";
import { useRouter } from "next/navigation";
import { MicVocal, Trash2, Plus } from "lucide-react";

import { createNarration } from "../../actions/narrate";
import { deleteProject } from "../../actions/audiobook";
import { Script } from "../../actions/script";
import { AudiobookJob } from "../../actions/job";
import GenerateScriptModal from "./GenerateScriptModal";

interface ScriptControlsProps {
  narrationUrlPromise: Promise<string | null>;
  hasScripts: boolean;
  firstScriptFilename?: string;
  jobStatePromise: Promise<AudiobookJob | null>;
}

export default function ScriptControls({
  narrationUrlPromise,
  hasScripts,
  firstScriptFilename,
  jobStatePromise,
}: ScriptControlsProps) {
  const router = useRouter();
  const [isCreatingNarration, setIsCreatingNarration] = useState(false);
  const [isDeletingProject, setIsDeletingProject] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [existingScript, setExistingScript] = useState<Script | null>(null);

  const narrationUrl = use(narrationUrlPromise);
  const jobState = use(jobStatePromise);

  // Load the first script for character voice mapping when modal opens
  const handleOpenModal = async () => {
    if (hasScripts && firstScriptFilename) {
      try {
        const { getUserScript } = await import("../../actions/script");
        const script = await getUserScript(firstScriptFilename);
        setExistingScript(script);
      } catch (error) {
        console.error("Error loading existing script:", error);
      }
    }
    setIsModalOpen(true);
  };

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
                  : handleOpenModal
              }
              title="Add New Chapter"
            >
              <Plus className="h-5 w-5" />
            </a>
          </li>
          <li>
            <a
              className={`${
                !hasScripts ||
                isCreatingNarration ||
                isProcessing ||
                isDeletingProject
                  ? "disabled cursor-not-allowed opacity-50"
                  : "cursor-pointer"
              } font-medium`}
              onClick={
                !hasScripts ||
                isCreatingNarration ||
                isProcessing ||
                isDeletingProject
                  ? undefined
                  : handleCreateNarration
              }
              title={
                !hasScripts
                  ? "No scripts available"
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
                (!hasScripts && !narrationUrl) || isDeletingProject || isProcessing
                  ? "disabled cursor-not-allowed opacity-50"
                  : "cursor-pointer"
              } font-medium`}
              onClick={
                (!hasScripts && !narrationUrl) || isDeletingProject || isProcessing
                  ? undefined
                  : handleDeleteProject
              }
              title={
                !hasScripts && !narrationUrl
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
        existingScript={existingScript}
      />
    </>
  );
}
