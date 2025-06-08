"use client";

import React from "react";
import { use, useState } from "react";
import { useRouter } from "next/navigation";

import { createNarration } from "../actions/narrate";
import { deleteProject } from "../actions/audiobook";
import { Script } from "../actions/script";
import { AudiobookJob } from "../actions/job";
import ControlButton from "./ControlButton";

interface ControlsClientProps {
  narrationUrlPromise: Promise<string | null>;
  scriptPromise: Promise<Script | null>;
  jobStatePromise: Promise<AudiobookJob | null>;
}

export default function ControlsClient({
  narrationUrlPromise,
  scriptPromise,
  jobStatePromise,
}: ControlsClientProps) {
  const router = useRouter();
  const [isCreatingNarration, setIsCreatingNarration] = useState(false);
  const [isDeletingProject, setIsDeletingProject] = useState(false);

  const narrationUrl = use(narrationUrlPromise);
  const script = use(scriptPromise);
  const jobState = use(jobStatePromise);

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

  return (
    <div className="flex gap-4 ml-auto">
      {script && !narrationUrl && (
        <ControlButton
          disabled={
            isCreatingNarration ||
            jobState?.script_status === "processing" ||
            jobState?.narration_status === "processing"
          }
          onClick={handleCreateNarration}
          variant="primary"
          className="ml-auto"
        >
          {isCreatingNarration || jobState?.narration_status === "processing"
            ? "Creating Narration..."
            : "Narrate"}
        </ControlButton>
      )}
      {(script || narrationUrl) && (
        <ControlButton
          disabled={
            isDeletingProject ||
            jobState?.script_status === "processing" ||
            jobState?.narration_status === "processing"
          }
          onClick={handleDeleteProject}
          variant="destructive"
          className="ml-auto"
        >
          {isDeletingProject ? "Deleting Project..." : "Delete Project"}
        </ControlButton>
      )}
    </div>
  );
}
