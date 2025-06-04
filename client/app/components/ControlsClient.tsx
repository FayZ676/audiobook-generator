"use client";

import React from "react";
import { use, useState } from "react";
import { useRouter } from "next/navigation";

import { createNarration } from "../actions/narrate";
import { deleteProject } from "../actions/audiobook";
import { Script } from "../actions/script";

interface ControlsClientProps {
  narrationUrlPromise: Promise<string | null>;
  scriptPromise: Promise<Script | null>;
}

export default function ControlsClient({
  narrationUrlPromise,
  scriptPromise,
}: ControlsClientProps) {
  const router = useRouter();
  const [isCreatingNarration, setIsCreatingNarration] = useState(false);
  const [isDeletingProject, setIsDeletingProject] = useState(false);

  const narrationUrl = use(narrationUrlPromise);
  const script = use(scriptPromise);

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
    <div className="flex gap-4">
      {script && !narrationUrl && (
        <button
          disabled={isCreatingNarration}
          onClick={handleCreateNarration}
          className="ml-auto border py-2 px-4 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isCreatingNarration ? "Creating Narration..." : "Narrate"}
        </button>
      )}
      {(script || narrationUrl) && (
        <button
          disabled={isDeletingProject}
          onClick={handleDeleteProject}
          className="ml-auto border py-2 px-4 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isDeletingProject ? "Deleting Project..." : "Delete Project"}
        </button>
      )}
    </div>
  );
}
