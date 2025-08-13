import React, { Suspense } from "react";

import { getJobState } from "../../actions/job";
import { getVoices } from "../../actions/voices";
import { getCurrentProject } from "../../actions/project";
import { getChapters } from "../../actions/chapter";
import { getScript } from "../../actions/script";
import { getNarration } from "../../actions/narrate";
import { getAudioManifest } from "../../actions/segments";
import { AudioSegmentData } from "../../types";

import ProjectDashboardWrapper from "@/app/components/project/ProjectDashboardWrapper";

interface ProjectDashboardProps {
  currentChapter?: string;
  initialChapters?: string[];
}

export default async function ProjectDashboard({
  currentChapter,
  initialChapters,
}: ProjectDashboardProps) {
  const selectedChapter = currentChapter || null;

  const jobStatePromise = getJobState();
  const voicesPromise = getVoices();
  const projectPromise = getCurrentProject();
  const chaptersPromise = initialChapters
    ? Promise.resolve(initialChapters)
    : getChapters();
  const scriptPromise = selectedChapter
    ? getScript(selectedChapter)
    : Promise.resolve(null);
  const narrationPromise = selectedChapter
    ? getNarration(selectedChapter)
    : Promise.resolve(null);
  const audioSegmentDataPromise: Promise<AudioSegmentData> = selectedChapter
    ? getAudioManifest(selectedChapter)
        .then((m) => ({
          ids: m.segments.map((s) => s.id),
          urls: Object.fromEntries(m.segments.map((s) => [s.id, s.url])),
        }))
        .catch(() => ({ ids: [], urls: {} }))
    : Promise.resolve({
        ids: [] as string[],
        urls: {} as Record<string, string>,
      });

  return (
    <Suspense
      fallback={
        <div>
          Loading project{" "}
          <span className="loading loading-dots loading-xs"></span>
        </div>
      }
    >
      <ProjectDashboardWrapper
        voicesPromise={voicesPromise}
        jobStatePromise={jobStatePromise}
        projectPromise={projectPromise}
        chaptersPromise={chaptersPromise}
        scriptPromise={scriptPromise}
        narrationPromise={narrationPromise}
        selectedChapter={selectedChapter}
        audioSegmentDataPromise={audioSegmentDataPromise}
      />
    </Suspense>
  );
}
