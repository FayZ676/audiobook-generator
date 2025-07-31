import React, { Suspense } from "react";

import { getJobState } from "../../actions/job";
import { getVoices } from "../../actions/voices";
import { getCurrentProject } from "../../actions/project";
import { getChapters } from "../../actions/chapter";
import { getScript } from "../../actions/script";
import { getNarration } from "../../actions/narrate";

import ChapterProjectManagerClient from "../chapter/ChapterProjectManagerClient";

export default async function ChapterProjectManager() {
  const jobStatePromise = getJobState();
  const voicesPromise = getVoices();
  const projectPromise = getCurrentProject();
  const chaptersPromise = getChapters();

  const chapters = await chaptersPromise;
  const firstChapter = chapters.length > 0 ? chapters[0] : null;

  const scriptPromise = firstChapter
    ? getScript(firstChapter)
    : Promise.resolve(null);
  const narrationPromise = firstChapter
    ? getNarration(firstChapter)
    : Promise.resolve(null);

  return (
    <Suspense
      fallback={
        <div>
          Loading project{" "}
          <span className="loading loading-dots loading-xs"></span>
        </div>
      }
    >
      <ChapterProjectManagerClient
        voicesPromise={voicesPromise}
        jobStatePromise={jobStatePromise}
        projectPromise={projectPromise}
        chaptersPromise={chaptersPromise}
        scriptPromise={scriptPromise}
        narrationPromise={narrationPromise}
        firstChapter={firstChapter}
      />
    </Suspense>
  );
}
