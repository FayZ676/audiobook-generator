import React from "react";

import { getScript } from "../../actions/script";
import { getNarration } from "../../actions/narrate";
import { getJobState } from "../../actions/job";
import { getVoices } from "../../actions/voices";
import { getCurrentProject } from "../../actions/project";

import ProjectManager from "./ProjectManager";
import NarrationSection from "@/app/components/narration/NarrationSection";
import JobStateSection from "./JobStateSection";

export default function ProjectDashboard() {
  const scriptPromise = getScript();
  const narrationUrlPromise = getNarration();
  const jobStatePromise = getJobState();
  const voicesPromise = getVoices();
  const projectPromise = getCurrentProject();

  return (
    <div className="flex flex-col gap-4">
      <JobStateSection
        jobStatePromise={jobStatePromise}
        scriptPromise={scriptPromise}
      />
      <NarrationSection narrationUrlPromise={narrationUrlPromise} />
      <ProjectManager
        scriptPromise={scriptPromise}
        voicesPromise={voicesPromise}
        narrationUrlPromise={narrationUrlPromise}
        jobStatePromise={jobStatePromise}
        projectPromise={projectPromise}
      />
    </div>
  );
}
