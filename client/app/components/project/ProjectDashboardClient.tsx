"use client";

import React, { useState, use, useEffect } from "react";
import { useRouter } from "next/navigation";

import { usePusherSubscriptions } from "@/app/hooks/usePusherSubscriptions";
import { useUserChannels } from "@/app/lib/pusher-channels";
import { handleRevalidateTag } from "@/app/actions/revalidate";

import { Menu } from "lucide-react";

import { Voice } from "../../actions/voices";
import { AudiobookJob } from "../../actions/job";
import { Script } from "../../actions/script";
import { deleteProject } from "../../actions/audiobook";

import ChapterContent from "../chapter/ChapterContent";
import GenerateScriptForm from "../script/GenerateScriptForm";
import CreateProjectForm from "./CreateProjectForm";
import ChapterSelector from "../chapter/ChapterSelector";
import CreateChapterForm from "../chapter/CreateChapterForm";
import JobStateSection from "../job/JobStateSection";
import VoicesDashboardClient from "../voices/VoicesDashboardClient";

interface ProjectDashboardClientProps {
  voicesPromise: Promise<Voice[]>;
  jobStatePromise: Promise<AudiobookJob | null>;
  projectPromise: Promise<{
    name: string;
    user_id: string; // NOTE (faizi): We can get this from clerk.
  } | null>;
  chaptersPromise: Promise<string[]>;
  scriptPromise: Promise<Script | null>;
  narrationPromise: Promise<string | null>;
  selectedChapter: string | null;
}

export default function ProjectDashboardClient({
  voicesPromise,
  jobStatePromise,
  projectPromise,
  chaptersPromise,
  scriptPromise,
  narrationPromise,
  selectedChapter,
}: ProjectDashboardClientProps) {
  const router = useRouter();
  const [isEditing, setIsEditing] = useState(false);
  const [isDeletingProject, setIsDeletingProject] = useState(false);

  const voices = use(voicesPromise);
  const project = use(projectPromise);
  const chapters = use(chaptersPromise);
  const currentScript = use(scriptPromise);
  const narrationUrl = use(narrationPromise);
  const userChannels = useUserChannels();

  const handleRevalidate = () => {
    handleRevalidateTag("script");
    handleRevalidateTag("narration");
    handleRevalidateTag("chapters");
    handleRevalidateTag("project");
    router.refresh();
  };

  usePusherSubscriptions({
    channels: userChannels
      ? [userChannels.SCRIPT_CHANNEL, userChannels.SPEECH_CHANNEL]
      : [],
    onUpdate: handleRevalidate,
  });

  useEffect(() => {
    if (!selectedChapter && project && chapters.length > 0) {
      router.push(`/project/${encodeURIComponent(chapters[0])}`);
    } else if (
      selectedChapter &&
      chapters.length > 0 &&
      !chapters.includes(selectedChapter)
    ) {
      router.push("/project");
    }
  }, [selectedChapter, project, chapters, router]);

  const handleChapterSelect = (chapter: string) => {
    router.push(`/project/${encodeURIComponent(chapter)}`);
    setIsEditing(false);
  };

  const handleChapterCreatedOrDeleted = () => {
    handleRevalidate();
  };

  const handleDeleteProject = async () => {
    setIsDeletingProject(true);
    await deleteProject();
    router.refresh();
  };

  if (!project) {
    return <CreateProjectForm />;
  }

  const hasNoSelectedChapter = !selectedChapter;
  const hasNoScript = !currentScript;

  return (
    <div className="flex h-screen">
      <div className="drawer">
        <input id="my-drawer" type="checkbox" className="drawer-toggle" />
        <div className="drawer-content">
          <div className="flex-1 flex flex-col">
            <div className="flex-1 p-4 space-y-4 overflow-y-auto">
              <JobStateSection
                jobStatePromise={jobStatePromise}
                scriptPromise={scriptPromise}
              />

              <div className="space-y-4">
                <div className="flex justify-between items-center mb-4">
                  <div className="flex gap-4 items-center">
                    <label htmlFor="my-drawer" className="btn drawer-button">
                      <Menu size={16} />
                    </label>
                    <h3 className="font-bold">{project.name}</h3>
                  </div>

                  {selectedChapter && (
                    <h4 className="font-semibold">{selectedChapter}</h4>
                  )}
                </div>

                {hasNoSelectedChapter && chapters.length === 0 && (
                  <CreateChapterForm
                    onChapterCreated={handleChapterCreatedOrDeleted}
                  />
                )}

                {selectedChapter && hasNoScript && (
                  <GenerateScriptForm chapterName={selectedChapter} />
                )}

                {selectedChapter && !hasNoScript && (
                  <ChapterContent
                    selectedChapter={selectedChapter}
                    currentScript={currentScript}
                    narrationUrl={narrationUrl}
                    narrationPromise={narrationPromise}
                    scriptPromise={scriptPromise}
                    jobStatePromise={jobStatePromise}
                    voicesPromise={voicesPromise}
                    voices={voices}
                    isEditing={isEditing}
                    setIsEditing={setIsEditing}
                  />
                )}
              </div>
            </div>
          </div>
        </div>
        <div className="drawer-side">
          <label
            htmlFor="my-drawer"
            aria-label="close sidebar"
            className="drawer-overlay"
          ></label>
          <ul className="flex flex-col gap-8 menu bg-base-200 min-h-full w-90 p-4">
            <li>
              <div className="flex flex-col p-0 hover:bg-transparent active:!bg-transparent active:!text-base-content">
                <ChapterSelector
                  chapters={chapters}
                  onChapterSelect={handleChapterSelect}
                />
                <CreateChapterForm
                  onChapterCreated={handleChapterCreatedOrDeleted}
                />
              </div>
            </li>
            <li>
              <div className="flex flex-col p-0 hover:bg-transparent active:!bg-transparent active:!text-base-content">
                <VoicesDashboardClient voicesPromise={voicesPromise} />
              </div>
            </li>
            <li className="mt-auto">
              <button
                onClick={handleDeleteProject}
                disabled={isDeletingProject}
                className="btn btn-outline btn-error btn-block"
                title={
                  isDeletingProject ? "Deleting Project..." : "Delete Project"
                }
              >
                Delete Project
              </button>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
