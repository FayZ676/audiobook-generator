import React, { Suspense } from "react";

import { getJobState } from "../../actions/job";
import { getVoices } from "../../actions/voices";
import { getCurrentProject } from "../../actions/project";
import { getChapters } from "../../actions/chapter";
import { getScript } from "../../actions/script";
import { getNarration } from "../../actions/narrate";
import { getAudioManifest } from "../../actions/segments";

import ProjectDashboardClient from "./ProjectDashboardClient";

interface ProjectDashboardProps {
  currentChapter?: string;
  initialChapters?: string[];
}

export default async function ProjectDashboard({
  currentChapter,
  initialChapters,
}: ProjectDashboardProps) {
  const jobStatePromise = getJobState();
  const voicesPromise = getVoices();
  const projectPromise = getCurrentProject();
  const chaptersPromise = initialChapters
    ? Promise.resolve(initialChapters)
    : getChapters();

  const selectedChapter = currentChapter || null;

  const scriptPromise = selectedChapter
    ? getScript(selectedChapter)
    : Promise.resolve(null);
  const narrationPromise = selectedChapter
    ? getNarration(selectedChapter)
    : Promise.resolve(null);
  const audioSegmentIdsPromise = selectedChapter
    ? getAudioManifest(selectedChapter)
        .then((m) => m.segments.map((s) => s.id))
        .catch(() => [])
    : Promise.resolve<string[]>([]);

  return (
    <Suspense
      fallback={
        <div>
          Loading project{" "}
          <span className="loading loading-dots loading-xs"></span>
        </div>
      }
    >
      <ProjectDashboardClient
        voicesPromise={voicesPromise}
        jobStatePromise={jobStatePromise}
        projectPromise={projectPromise}
        chaptersPromise={chaptersPromise}
        scriptPromise={scriptPromise}
        narrationPromise={narrationPromise}
        selectedChapter={selectedChapter}
        audioSegmentIdsPromise={audioSegmentIdsPromise}
      />
    </Suspense>
  );
}
