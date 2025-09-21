"use client";

import React, { use, useState, Suspense } from "react";
import { useRouter, useParams } from "next/navigation";

import { usePusherSubscriptions } from "@/app/hooks/usePusherSubscriptions";
import { getUserSpecificChannels } from "@/app/lib/pusher-channels";
import { handleRevalidateTag } from "@/app/actions/revalidate";

import { Menu } from "lucide-react";

import type { Script } from "../../actions/script";
import { deleteProject } from "../../actions/audiobook";
import type { AudiobookJob } from "../../actions/job";
import type { Voice } from "../../actions/voices";
import type { NarrationUrl } from "@/app/actions/narrate";

import GenerateScriptForm from "../script/GenerateScriptForm";

import ChapterSelector from "../chapter/ChapterSelector";
import CreateChapterForm from "../chapter/CreateChapterForm";
import JobStateClient from "../job/JobStateClient";
import VoicesDashboardClient from "../voices/VoicesDashboardClient";
import CreateProjectForm from "./CreateProjectForm";
import ScriptEditor from "../script/ScriptEditor";

interface ProjectDashboardClientProps {
  userId: string;
  projectName: string;
  chapters: string[];
  jobStatePromise: Promise<AudiobookJob | null>;
  voicesPromise: Promise<Voice[]>;
  scriptPromise?: Promise<Script | null> | null;
  narrationPromise?: Promise<NarrationUrl | null> | null;
}

export default function ProjectDashboardClient({
  userId,
  projectName,
  chapters: propChapters,
  jobStatePromise,
  voicesPromise,
  scriptPromise,
  narrationPromise,
}: ProjectDashboardClientProps) {
  const router = useRouter();
  const params = useParams();
  const [isDeletingProject, setIsDeletingProject] = useState(false);

  const selectedChapter = params.chapter
    ? decodeURIComponent(params.chapter as string)
    : null;
  const chapters = propChapters || [];
  const currentScript =
    selectedChapter && scriptPromise ? use(scriptPromise) : null;
  const userChannels = getUserSpecificChannels(userId);

  const handleRevalidate = async () => {
    await Promise.all([
      handleRevalidateTag("script"),
      handleRevalidateTag("narration"),
      handleRevalidateTag("chapters"),
      handleRevalidateTag("project"),
      handleRevalidateTag("job"),
    ]);
    router.refresh();
  };

  usePusherSubscriptions({
    channels: [userChannels.SCRIPT_CHANNEL, userChannels.SPEECH_CHANNEL],
    onUpdate: handleRevalidate,
  });

  const handleChapterSelect = (chapter: string) => {
    router.push(`/project/${encodeURIComponent(chapter)}`);
  };

  if (!projectName) {
    return <CreateProjectForm />;
  }

  const handleChapterCreatedOrDeleted = () => {
    handleRevalidate();
  };

  const handleDeleteProject = async () => {
    setIsDeletingProject(true);
    await deleteProject();
    router.refresh();
  };

  const hasNoSelectedChapter = !selectedChapter;
  const hasNoScript = !currentScript;

  return (
    <div className="flex h-screen">
      <div className="drawer">
        <input id="my-drawer" type="checkbox" className="drawer-toggle" />
        <div className="drawer-content">
          <div className="flex-1 flex flex-col">
            <div className="flex-1 space-y-4 overflow-y-auto">
              <Suspense fallback={<div>Loading job state...</div>}>
                <JobStateClient
                  userId={userId}
                  jobStatePromise={jobStatePromise}
                />
              </Suspense>

              <div className="space-y-8">
                <div className="flex justify-between">
                  <div className="flex gap-4 items-center">
                    <label htmlFor="my-drawer" className="btn drawer-button">
                      <Menu size={16} />
                    </label>
                    <h3 className="mt-0 mb-0">{projectName}</h3>
                  </div>
                  {selectedChapter && (
                    <div className="flex items-center ">
                      <h4 className="mt-0 mb-0">{selectedChapter}</h4>
                    </div>
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
                  <Suspense fallback={<div>Loading script editor...</div>}>
                    <ScriptEditor
                      scriptPromise={scriptPromise as Promise<Script | null>}
                      jobStatePromise={jobStatePromise}
                      narrationPromise={
                        selectedChapter
                          ? (narrationPromise as Promise<NarrationUrl | null>)
                          : Promise.resolve(null)
                      }
                      voicesPromise={voicesPromise}
                    />
                  </Suspense>
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
          <ul className="flex flex-col gap-8 menu bg-base-200 min-h-full w-90 p-4 mt-0">
            <li>
              <h4>Chapters</h4>
              <div className="flex flex-col p-0 hover:bg-transparent active:!bg-transparent active:!text-base-content">
                <ChapterSelector
                  chapters={chapters}
                  onChapterSelect={handleChapterSelect}
                  onChapterDeleted={handleChapterCreatedOrDeleted}
                />
                <CreateChapterForm
                  onChapterCreated={handleChapterCreatedOrDeleted}
                />
              </div>
            </li>
            <li>
              <div className="flex flex-col p-0 hover:bg-transparent active:!bg-transparent active:!text-base-content">
                <Suspense fallback={<div>Loading voices...</div>}>
                  <VoicesDashboardClient voicesPromise={voicesPromise} />
                </Suspense>
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
