"use client";

import React, { use, useEffect } from "react";
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
import ChapterSelector from "../chapter/ChapterSelector";
import CreateChapterForm from "../chapter/CreateChapterForm";
import JobStateSection from "../job/JobStateSection";
import VoicesDashboardClient from "../voices/VoicesDashboardClient";

interface ProjectDashboardClientProps {
  voicesPromise: Promise<Voice[]>;
  jobStatePromise: Promise<AudiobookJob | null>;
  project: {
    name: string;
    user_id: string; // NOTE (faizi): We can get this from clerk.
  };
  chaptersPromise: Promise<string[]>;
  scriptPromise: Promise<Script | null>;
  narrationPromise: Promise<string | null>;
  selectedChapter: string | null;
  audioSegmentIdsPromise: Promise<string[]>;
}

export default function ProjectDashboardClient({
  voicesPromise,
  jobStatePromise,
  project,
  chaptersPromise,
  scriptPromise,
  narrationPromise,
  selectedChapter,
  audioSegmentIdsPromise,
}: ProjectDashboardClientProps) {
  const router = useRouter();
  const [isDeletingProject, setIsDeletingProject] = React.useState(false);

  const voices = use(voicesPromise);
  const chapters = use(chaptersPromise);
  const currentScript = use(scriptPromise);
  const narrationUrl = use(narrationPromise);
  const audioSegmentIds = use(audioSegmentIdsPromise);
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
            <div className="flex-1 p-4 space-y-4 overflow-y-auto">
              <JobStateSection
                jobStatePromise={jobStatePromise}
                scriptPromise={scriptPromise}
              />

              <div className="space-y-8">
                <div className="flex justify-between">
                  <div className="flex gap-4 items-center">
                    <label htmlFor="my-drawer" className="btn drawer-button">
                      <Menu size={16} />
                    </label>
                    <h3 className="mt-0 mb-0">{project.name}</h3>
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
                  <ChapterContent
                    selectedChapter={selectedChapter}
                    currentScript={currentScript}
                    narrationUrl={narrationUrl}
                    narrationPromise={narrationPromise}
                    scriptPromise={scriptPromise}
                    jobStatePromise={jobStatePromise}
                    voicesPromise={voicesPromise}
                    audioSegmentIds={audioSegmentIds}
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
