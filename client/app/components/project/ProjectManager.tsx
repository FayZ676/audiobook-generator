import React, { Suspense } from "react";

import { Script } from "../../actions/script";
import { Voice } from "../../actions/voices";
import { AudiobookJob } from "../../actions/job";

import ProjectManagerClient from "../project/ProjectManagerClient";

interface ProjectManagerProps {
  scriptPromise: Promise<Script | null>;
  voicesPromise: Promise<Voice[]>;
  narrationUrlPromise: Promise<string | null>;
  jobStatePromise: Promise<AudiobookJob | null>;
  projectPromise: Promise<{ name: string; created_at: string } | null>;
}

export default function ProjectManager({
  scriptPromise,
  voicesPromise,
  narrationUrlPromise,
  jobStatePromise,
  projectPromise,
}: ProjectManagerProps) {
  return (
    <Suspense
      fallback={
        <div>
          Loading project{" "}
          <span className="loading loading-dots loading-xs"></span>
        </div>
      }
    >
      <ProjectManagerClient
        scriptPromise={scriptPromise}
        voicesPromise={voicesPromise}
        narrationUrlPromise={narrationUrlPromise}
        jobStatePromise={jobStatePromise}
        projectPromise={projectPromise}
      />
    </Suspense>
  );
}
