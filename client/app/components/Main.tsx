import React from "react";

import { deleteProject } from "@/app/actions/audiobook";

import ScriptSection from "@/app/components/ScriptSection";
import NarrationSection from "@/app/components/NarrationSection";
import JobStateSection from "./JobStateSection";

export default function Main() {
  return (
    <div className="flex flex-col gap-4">
      <JobStateSection />
      <form action={deleteProject}>
        <button className="ml-auto border py-2 px-4">Delete Project</button>
      </form>
      <NarrationSection />
      <ScriptSection />
    </div>
  );
}
