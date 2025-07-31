"use client";

import React, { useState, use } from "react";
import { useRouter } from "next/navigation";

import { usePusherSubscriptions } from "@/app/hooks/usePusherSubscriptions";
import { useUserChannels } from "@/app/lib/pusher-channels";
import { handleRevalidateTag } from "@/app/actions/revalidate";

import { Menu } from "lucide-react";

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
      <div className="drawer">
        <input id="my-drawer" type="checkbox" className="drawer-toggle" />
        <div className="drawer-content">
          {/* Main Content */}
          <div className="flex-1 flex flex-col">
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
                    Create a new chapter or select an existing one to get
                    started.
                  </p>
                </div>
              ) : !currentScript ? (
                <div className="space-y-4">
                  <div className="text-center">
                    <div className="flex justify-between">
                      <h4 className="text-lg font-semibold">
                        {selectedChapter}
                      </h4>
                    </div>
                    <p className="text-base-content/60 mb-4">
                      Generate a script for this chapter to get started.
                    </p>
                  </div>
                  <GenerateScriptForm chapterName={selectedChapter!} />
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="flex justify-between items-center mb-4">
                    <div className="flex gap-4 items-center">
                      <label htmlFor="my-drawer" className="btn drawer-button">
                        <Menu size={16} />
                      </label>
                      <h3 className="text-lg font-bold">{project.name}</h3>
                    </div>
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

                  {narrationUrl && (
                    <NarrationAudio narrationUrl={narrationUrl} />
                  )}

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
        </div>
        <div className="drawer-side">
          <label
            htmlFor="my-drawer"
            aria-label="close sidebar"
            className="drawer-overlay"
          ></label>
          <ul className="menu bg-base-200 text-base-content min-h-full w-80 p-4">
            {/* Sidebar content here */}
            <li>
              <div className="flex flex-col gap-4">
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
            </li>
            <li>
              <VoicesDashboardClient voicesPromise={voicesPromise} />
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
