import React from "react";

import { getScript } from "../actions/script";
import { getNarration } from "../actions/narrate";
import { getJobState } from "../actions/job";
import { getVoices } from "../actions/voices";

import ScriptSection from "@/app/components/ScriptSection";
import NarrationSection from "@/app/components/NarrationSection";
import JobStateSection from "./JobStateSection";
import ControlsSection from "./ControlsSection";

export default function ProjectDashboard() {
  const scriptPromise = getScript();
  const narrationUrlPromise = getNarration();
  const jobStatePromise = getJobState();
  const voicesPromise = getVoices();

  return (
    <div className="flex flex-col gap-4">
      <ControlsSection
        narrationUrlPromise={narrationUrlPromise}
        scriptPromise={scriptPromise}
        jobStatePromise={jobStatePromise}
      />
      <JobStateSection jobStatePromise={jobStatePromise} />
      <NarrationSection narrationUrlPromise={narrationUrlPromise} />
      <ScriptSection
        scriptPromise={scriptPromise}
        voicesPromise={voicesPromise}
      />
    </div>
  );
}
