import React from "react";

import { listUserScripts } from "../../actions/script";
import { getNarration } from "../../actions/narrate";
import { getJobState } from "../../actions/job";
import { getVoices } from "../../actions/voices";

import ScriptManager from "@/app/components/script/ScriptManager";
import NarrationSection from "@/app/components/narration/NarrationSection";
import JobStateSection from "./JobStateSection";

export default function ProjectDashboard() {
  const scriptsPromise = listUserScripts();
  const narrationUrlPromise = getNarration();
  const jobStatePromise = getJobState();
  const voicesPromise = getVoices();

  return (
    <div className="flex flex-col gap-4">
      <JobStateSection 
        jobStatePromise={jobStatePromise} 
        scriptsPromise={scriptsPromise}
      />
      <NarrationSection narrationUrlPromise={narrationUrlPromise} />
      <ScriptManager
        scriptsPromise={scriptsPromise}
        voicesPromise={voicesPromise}
        narrationUrlPromise={narrationUrlPromise}
        jobStatePromise={jobStatePromise}
      />
    </div>
  );
}
