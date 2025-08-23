"use client";

import React, { use, useEffect, useState, Suspense } from "react";
import { useRouter, useParams } from "next/navigation";

import { usePusherSubscriptions } from "@/app/hooks/usePusherSubscriptions";
import { useUserChannels } from "@/app/lib/pusher-channels";
import { handleRevalidateTag } from "@/app/actions/revalidate";

import { Menu } from "lucide-react";

import { getCurrentProject } from "../../actions/project";
import { getChapters } from "../../actions/chapter";
import { getScript } from "../../actions/script";
import { deleteProject } from "../../actions/audiobook";

import GenerateScriptForm from "../script/GenerateScriptForm";

import ChapterSelector from "../chapter/ChapterSelector";
import CreateChapterForm from "../chapter/CreateChapterForm";
import JobStateClient from "../job/JobStateClient";
import VoicesDashboardClient from "../voices/VoicesDashboardClient";
import CreateProjectForm from "./CreateProjectForm";
import ScriptEditor from "../script/ScriptEditor";

export default function ProjectDashboardClient() {
  return (
    <Suspense fallback={<div>Loading Project...</div>}>
      <ProjectDashboardContent />
    </Suspense>
  );
}

function ProjectDashboardContent() {
  const router = useRouter();
  const params = useParams();
  const [isClient, setIsClient] = useState(false);
  const [isDeletingProject, setIsDeletingProject] = useState(false);

  const selectedChapter = params.chapter
    ? decodeURIComponent(params.chapter as string)
    : null;

  const project = use(getCurrentProject());
  const chapters = use(getChapters());
  const currentScript = selectedChapter
    ? use(getScript(selectedChapter))
    : null;
  const userChannels = useUserChannels();

  const handleRevalidate = async () => {
    await Promise.all([
      handleRevalidateTag("script"),
      handleRevalidateTag("narration"),
      handleRevalidateTag("chapters"),
      handleRevalidateTag("project"),
      handleRevalidateTag("job"),
      handleRevalidateTag("audio-manifest"),
    ]);
    router.refresh();
  };

  useEffect(() => {
    setIsClient(true);
  }, []);

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
  };

  if (!project) {
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
                <JobStateClient />
              </Suspense>

              <div className="space-y-8">
                <div className="flex justify-between">
                  <div className="flex gap-4 items-center">
                    <label htmlFor="my-drawer" className="btn drawer-button">
                      <Menu size={16} />
                    </label>
                    {/* TODO: Why does only this suffer from hydration errors? */}
                    {isClient && <h3 className="mt-0 mb-0">{project.name}</h3>}
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
                  <Suspense fallback={<div>Loading Script Editor...</div>}>
                    <ScriptEditor />
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
                  <VoicesDashboardClient />
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
