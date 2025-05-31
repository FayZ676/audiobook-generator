import React from "react";

import { deleteProject } from "@/app/actions/audiobook";

import { getScript } from "../actions/script";
import { getNarration } from "../actions/narrate";
import { getJobState } from "../actions/job";

import ScriptSection from "@/app/components/ScriptSection";
import NarrationSection from "@/app/components/NarrationSection";
import JobStateSection from "./JobStateSection";
import NarrationButton from "./NarrationButton";

export default function Main() {
  const scriptPromise = getScript();
  const narrationUrlPromise = getNarration();
  const jobStatePromise = getJobState();

  return (
    <div className="flex flex-col gap-4">
      <JobStateSection jobStatePromise={jobStatePromise} />
      <form action={deleteProject}>
        <button className="ml-auto border py-2 px-4">Delete Project</button>
      </form>
      <NarrationButton />
      <NarrationSection narrationUrlPromise={narrationUrlPromise} />
      <ScriptSection scriptPromise={scriptPromise} />
    </div>
  );
}
