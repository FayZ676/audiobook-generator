"use client";

import React from "react";
import { use, useState } from "react";
import { useRouter } from "next/navigation";
import { Mic, Trash2 } from "lucide-react";

import { createNarration } from "../actions/narrate";
import { deleteProject } from "../actions/audiobook";
import { Script } from "../actions/script";
import { AudiobookJob } from "../actions/job";

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
    <div className="flex justify-between items-center">
      <h3 className="font-bold">Project controls</h3>
      <ul className="menu menu-horizontal bg-base-200 rounded-box">
        {script && !narrationUrl && (
          <li>
            <a
              className={`${
                isCreatingNarration ||
                jobState?.script_status === "processing" ||
                jobState?.narration_status === "processing"
                  ? "disabled cursor-not-allowed opacity-50"
                  : "cursor-pointer"
              } font-medium`}
              onClick={
                isCreatingNarration ||
                jobState?.script_status === "processing" ||
                jobState?.narration_status === "processing"
                  ? undefined
                  : handleCreateNarration
              }
              title={
                isCreatingNarration ||
                jobState?.narration_status === "processing"
                  ? "Creating Narration..."
                  : "Narrate"
              }
            >
              <Mic className="h-5 w-5" />
            </a>
          </li>
        )}
        {(script || narrationUrl) && (
          <li>
            <a
              className={`${
                isDeletingProject ||
                jobState?.script_status === "processing" ||
                jobState?.narration_status === "processing"
                  ? "disabled cursor-not-allowed opacity-50"
                  : "cursor-pointer"
              } font-medium`}
              onClick={
                isDeletingProject ||
                jobState?.script_status === "processing" ||
                jobState?.narration_status === "processing"
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
  );
}
