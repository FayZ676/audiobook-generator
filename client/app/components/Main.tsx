import React from "react";

import { getScript } from "../actions/script";
import { getNarration } from "../actions/narrate";
import { getJobState } from "../actions/job";

import ScriptSection from "@/app/components/ScriptSection";
import NarrationSection from "@/app/components/NarrationSection";
import JobStateSection from "./JobStateSection";
import ControlsSection from "./ControlsSection";

export default function Main() {
  const scriptPromise = getScript();
  const narrationUrlPromise = getNarration();
  const jobStatePromise = getJobState();

  return (
    <div className="flex flex-col gap-4">
      <JobStateSection jobStatePromise={jobStatePromise} />
      <ControlsSection
        narrationUrlPromise={narrationUrlPromise}
        scriptPromise={scriptPromise}
      />
      <NarrationSection narrationUrlPromise={narrationUrlPromise} />
      <ScriptSection scriptPromise={scriptPromise} />
    </div>
  );
}
