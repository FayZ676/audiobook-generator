import React, { Suspense } from "react";

import { getScript } from "../../actions/script";
import { getNarration } from "../../actions/narrate";
import { getJobState } from "../../actions/job";
import { getVoices } from "../../actions/voices";
import { getCurrentProject } from "../../actions/project";
import { getChapters } from "../../actions/chapter";

import ChapterProjectManagerClient from "../chapter/ChapterProjectManagerClient";

export default function ChapterProjectManager() {
  const scriptPromiseFactory = async (chapterId: string) => {
    "use server";
    return getScript(chapterId);
  };
  const narrationUrlPromiseFactory = async (chapterId: string) => {
    "use server";
    return getNarration(chapterId);
  };
  const jobStatePromise = getJobState();
  const voicesPromise = getVoices();
  const projectPromise = getCurrentProject();
  const chaptersPromise = getChapters();

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
        scriptPromise={scriptPromiseFactory}
        voicesPromise={voicesPromise}
        narrationUrlPromise={narrationUrlPromiseFactory}
        jobStatePromise={jobStatePromise}
        projectPromise={projectPromise}
        chaptersPromise={chaptersPromise}
      />
    </Suspense>
  );
}
