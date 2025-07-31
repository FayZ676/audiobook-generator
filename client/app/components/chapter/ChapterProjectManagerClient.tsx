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
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

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
    setIsSidebarOpen(false);
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
      {/* Left Sidebar - Combined Chapters and Voices */}
      <div
        className={`${
          isSidebarOpen ? "translate-x-0" : "-translate-x-full"
        } fixed left-0 top-0 z-40 h-full w-80 bg-base-200 transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:z-auto`}
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="p-4 border-b border-base-300">
            <div className="lg:hidden flex justify-between items-center">
              <h4 className="font-semibold text-lg">Menu</h4>
              <button
                onClick={() => setIsSidebarOpen(false)}
                className="btn btn-ghost btn-sm"
              >
                ✕
              </button>
            </div>
          </div>

          {/* Content - Chapters and Voices vertically organized */}
          <div className="flex-1 p-4 overflow-y-auto space-y-6">
            {/* Chapters Section */}
            <div>
              <h5 className="font-semibold text-base mb-3 text-base-content/80">
                Chapters
              </h5>
              <div className="space-y-4">
                <ChapterSelector
                  chapters={chapters}
                  selectedChapter={selectedChapter}
                  onChapterSelect={handleChapterSelect}
                  onChapterDeleted={handleChapterCreatedOrDeleted}
                />
                <CreateChapterForm
                  onChapterCreated={handleChapterCreatedOrDeleted}
                />
              </div>
            </div>

            {/* Divider */}
            <div className="divider"></div>

            {/* Voices Section */}
            <div>
              <h5 className="font-semibold text-base mb-3 text-base-content/80">
                Voices
              </h5>
              <VoicesDashboardClient voicesPromise={voicesPromise} />
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Navbar */}
        <div className="navbar">
          {/* Sidebar Toggle */}
          <div className="flex-none lg:hidden">
            <button
              onClick={() => setIsSidebarOpen(true)}
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

          {/* Project Name */}
          <div className="mx-auto">
            <h3 className="font-bold text-lg">{project.name}</h3>
          </div>
        </div>

        {/* Content Area */}
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
      </div>

      {/* Overlay for mobile */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-20 lg:hidden"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}
    </div>
  );
}
