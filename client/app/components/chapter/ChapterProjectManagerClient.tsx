"use client";

import React, { useState, use } from "react";
import { useRouter } from "next/navigation";

import { usePusherSubscriptions } from "@/app/hooks/usePusherSubscriptions";
import { useUserChannels } from "@/app/lib/pusher-channels";
import { handleRevalidateTag } from "@/app/actions/revalidate";

import { Voice } from "../../actions/voices";
import { AudiobookJob } from "../../actions/job";
import { Script } from "../../actions/script";

import ScriptControls from "../script/ScriptControls";
import ScriptText from "../script/ScriptText";
import GenerateScriptForm from "../script/GenerateScriptForm";
import CreateProjectForm from "../project/CreateProjectForm";
import ChapterSelector from "../chapter/ChapterSelector";
import CreateChapterForm from "../chapter/CreateChapterForm";
import JobStateSection from "../project/JobStateSection";
import NarrationAudio from "../narration/NarrationAudio";

interface ChapterProjectManagerClientProps {
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

export default function ChapterProjectManagerClient({
  voicesPromise,
  jobStatePromise,
  projectPromise,
  chaptersPromise,
  scriptPromise,
  narrationPromise,
  selectedChapter,
}: ChapterProjectManagerClientProps) {
  const router = useRouter();
  const [isEditing, setIsEditing] = useState(false);

  const voices = use(voicesPromise);
  const project = use(projectPromise);
  const chapters = use(chaptersPromise);
  const currentScript = use(scriptPromise);
  const narrationUrl = use(narrationPromise);
  const userChannels = useUserChannels();

  usePusherSubscriptions({
    channels: userChannels
      ? [userChannels.SCRIPT_CHANNEL, userChannels.SPEECH_CHANNEL]
      : null,
    onUpdate: () => {
      handleRevalidateTag("script");
      handleRevalidateTag("narration");
      handleRevalidateTag("chapters");
      handleRevalidateTag("project");
      router.refresh();
    },
  });

  const handleChapterSelect = (chapter: string) => {
    router.push(`/project/${encodeURIComponent(chapter)}`);
    setIsEditing(false);

    const drawerToggle = document.getElementById(
      "chapter-drawer"
    ) as HTMLInputElement;
    if (drawerToggle) {
      drawerToggle.checked = false;
    }
  };

  const handleChapterCreatedOrDeleted = () => {
    handleRevalidateTag("chapters");
    handleRevalidateTag("project");
    router.refresh();
  };

  if (!project) {
    return <CreateProjectForm />;
  }

  return (
    <div className="drawer">
      <input id="chapter-drawer" type="checkbox" className="drawer-toggle" />

      {/* Main Content */}
      <div className="drawer-content flex flex-col">
        {/* Navbar with hamburger menu for all screen sizes */}
        <div className="navbar bg-base-100">
          <div className="flex-none">
            <label
              htmlFor="chapter-drawer"
              className="btn btn-square btn-ghost drawer-button"
            >
              <svg
                className="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 6h16M4 12h16M4 18h16"
                />
              </svg>
            </label>
          </div>
          <div className="flex-1">
            <h3 className="font-bold text-lg">{project.name}</h3>
          </div>
        </div>

        <div className="p-4 space-y-4">
          <JobStateSection
            jobStatePromise={jobStatePromise}
            scriptPromise={scriptPromise}
          />

          {!selectedChapter ? (
            <div className="text-center py-12">
              <h4 className="text-lg font-semibold mb-2">
                No Chapter Selected
              </h4>
              <p className="text-base-content/60">
                Create a new chapter or select an existing one to get started.
              </p>
            </div>
          ) : !currentScript ? (
            <div className="space-y-4">
              <div className="text-center">
                <h4 className="text-lg font-semibold mb-2">
                  {selectedChapter}
                </h4>
                <p className="text-base-content/60 mb-4">
                  Generate a script for this chapter to get started.
                </p>
              </div>
              <GenerateScriptForm chapterName={selectedChapter!} />
            </div>
          ) : (
            <div className="space-y-4">
              <div className="text-center">
                <h4 className="text-lg font-semibold">{selectedChapter}</h4>
              </div>

              <ScriptControls
                narrationUrlPromise={narrationPromise}
                scriptPromise={scriptPromise}
                jobStatePromise={jobStatePromise}
                voicesPromise={voicesPromise}
                isEditing={isEditing}
                onEditToggle={setIsEditing}
                chapterName={selectedChapter!}
              />

              {narrationUrl && <NarrationAudio narrationUrl={narrationUrl} />}

              <ScriptText
                script={currentScript}
                voices={voices}
                isEditing={isEditing}
                chapterName={selectedChapter!}
              />
            </div>
          )}
        </div>
      </div>

      {/* Drawer Sidebar */}
      <div className="drawer-side">
        <label
          htmlFor="chapter-drawer"
          className="drawer-overlay"
          aria-label="close sidebar"
        ></label>

        <aside className="min-h-full w-64 bg-base-200 p-4 space-y-4">
          <ChapterSelector
            chapters={chapters}
            selectedChapter={selectedChapter}
            onChapterSelect={handleChapterSelect}
            onChapterDeleted={handleChapterCreatedOrDeleted}
          />

          <CreateChapterForm onChapterCreated={handleChapterCreatedOrDeleted} />
        </aside>
      </div>
    </div>
  );
}
