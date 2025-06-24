import React from "react";

import { getScript } from "../actions/script";
import { getNarration } from "../actions/narrate";
import { getJobState } from "../actions/job";
import { getVoices } from "../actions/voices";

import ScriptManager from "@/app/components/ScriptManager";
import NarrationSection from "@/app/components/NarrationSection";
import JobStateSection from "./JobStateSection";

export default function ProjectDashboard() {
  const scriptPromise = getScript();
  const narrationUrlPromise = getNarration();
  const jobStatePromise = getJobState();
  const voicesPromise = getVoices();

  return (
    <div className="flex flex-col gap-4">
      <JobStateSection 
        jobStatePromise={jobStatePromise} 
        scriptPromise={scriptPromise}
      />
      <NarrationSection narrationUrlPromise={narrationUrlPromise} />
      <ScriptManager
        scriptPromise={scriptPromise}
        voicesPromise={voicesPromise}
        narrationUrlPromise={narrationUrlPromise}
        jobStatePromise={jobStatePromise}
      />
    </div>
  );
}
