"use client";

import React, { use } from "react";

import { Voice } from "../../actions/voices";
import { AudiobookJob } from "../../actions/job";
import { Script } from "../../actions/script";
import { AudioSegmentData, VoiceAudioData } from "../../types";

import ProjectDashboardClient from "./ProjectDashboardClient";
import CreateProjectForm from "./CreateProjectForm";

interface ProjectDashboardWrapperProps {
  voicesPromise: Promise<Voice[]>;
  voiceAudioData: VoiceAudioData;
  jobStatePromise: Promise<AudiobookJob | null>;
  projectPromise: Promise<{
    name: string;
    user_id: string;
  } | null>;
  chaptersPromise: Promise<string[]>;
  scriptPromise: Promise<Script | null>;
  narrationPromise: Promise<string | null>;
  selectedChapter: string | null;
  audioSegmentDataPromise: Promise<AudioSegmentData>;
}

export default function ProjectDashboardWrapper({
  voicesPromise,
  voiceAudioData,
  jobStatePromise,
  projectPromise,
  chaptersPromise,
  scriptPromise,
  narrationPromise,
  selectedChapter,
  audioSegmentDataPromise,
}: ProjectDashboardWrapperProps) {
  const project = use(projectPromise);

  if (!project) {
    return <CreateProjectForm />;
  }

  return (
    <ProjectDashboardClient
      voicesPromise={voicesPromise}
      voiceAudioData={voiceAudioData}
      jobStatePromise={jobStatePromise}
      project={project}
      chaptersPromise={chaptersPromise}
      scriptPromise={scriptPromise}
      narrationPromise={narrationPromise}
      selectedChapter={selectedChapter}
      audioSegmentDataPromise={audioSegmentDataPromise}
    />
  );
}
