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
    <div className="flex flex-col gap-4">
      <h3 className="font-bold text-center p-4">{project.name}</h3>

      <JobStateSection
        jobStatePromise={jobStatePromise}
        scriptPromise={scriptPromise}
      />

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        {/* Chapter Sidebar */}
        <div className="lg:col-span-1 space-y-4">
          <ChapterSelector
            chapters={chapters}
            selectedChapter={selectedChapter}
            onChapterSelect={handleChapterSelect}
            onChapterDeleted={handleChapterCreatedOrDeleted}
          />

          <CreateChapterForm onChapterCreated={handleChapterCreatedOrDeleted} />
        </div>

        {/* Main Content */}
        <div className="lg:col-span-3">
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
    </div>
  );
}
