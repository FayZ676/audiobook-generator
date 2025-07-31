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
import VoicesDashboardClient from "../voices/VoicesDashboardClient";

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
  const [isChapterSidebarOpen, setIsChapterSidebarOpen] = useState(false);
  const [isVoicesSidebarOpen, setIsVoicesSidebarOpen] = useState(false);

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
    setIsChapterSidebarOpen(false);
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
    <div className="flex h-screen">
      {/* Left Sidebar - Chapters */}
      <div
        className={`${
          isChapterSidebarOpen ? "translate-x-0" : "-translate-x-full"
        } fixed left-0 top-0 z-40 h-full w-64 bg-base-200 transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:z-auto`}
      >
        <div className="p-4 space-y-4 h-full overflow-y-auto">
          <div className="lg:hidden flex justify-between items-center mb-4">
            <h4 className="font-semibold text-lg">Chapters</h4>
            <button
              onClick={() => setIsChapterSidebarOpen(false)}
              className="btn btn-ghost btn-sm"
            >
              ✕
            </button>
          </div>

          <ChapterSelector
            chapters={chapters}
            selectedChapter={selectedChapter}
            onChapterSelect={handleChapterSelect}
            onChapterDeleted={handleChapterCreatedOrDeleted}
          />

          <CreateChapterForm onChapterCreated={handleChapterCreatedOrDeleted} />
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Navbar */}
        <div className="navbar bg-base-100 border-b">
          <div className="flex-none lg:hidden">
            <button
              onClick={() => setIsChapterSidebarOpen(true)}
              className="btn btn-square btn-ghost"
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
            </button>
          </div>
          <div className="flex-1">
            <h3 className="font-bold text-lg">{project.name}</h3>
          </div>
          <div className="flex-none">
            <button
              onClick={() => setIsVoicesSidebarOpen(!isVoicesSidebarOpen)}
              className="btn btn-square btn-ghost"
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
                  d="M12 6.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5Z"
                />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M7 16.5c0-1.5 2.5-3 5-3s5 1.5 5 3"
                />
              </svg>
            </button>
          </div>
        </div>

        {/* Content Area */}
        <div className="flex-1 flex">
          <div className="flex-1 p-4 space-y-4 overflow-y-auto">
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

          {/* Right Sidebar - Voices */}
          <div
            className={`${
              isVoicesSidebarOpen ? "translate-x-0" : "translate-x-full"
            } fixed right-0 top-0 z-30 h-full w-80 bg-base-200 transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:z-auto`}
          >
            <div className="p-4 h-full overflow-y-auto">
              <div className="flex justify-between items-center mb-4">
                <h4 className="font-semibold text-lg">Voices</h4>
                <button
                  onClick={() => setIsVoicesSidebarOpen(false)}
                  className="btn btn-ghost btn-sm lg:hidden"
                >
                  ✕
                </button>
              </div>
              <VoicesDashboardClient voicesPromise={voicesPromise} />
            </div>
          </div>
        </div>
      </div>

      {/* Overlay for mobile */}
      {(isChapterSidebarOpen || isVoicesSidebarOpen) && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-20 lg:hidden"
          onClick={() => {
            setIsChapterSidebarOpen(false);
            setIsVoicesSidebarOpen(false);
          }}
        />
      )}
    </div>
  );
}
