import React from "react";

import { createNarration } from "../actions/narrate";
import { deleteProject } from "../actions/audiobook";
import { Script } from "../actions/script";

interface ControlsSectionProps {
  narrationUrlPromise?: Promise<string | null>;
  scriptPromise?: Promise<Script | null>;
}

export default function ControlsSection({
  narrationUrlPromise,
  scriptPromise,
}: ControlsSectionProps) {
  return (
    <div>
      <form action={createNarration}>
        <button className="ml-auto border py-2 px-4">Narrate</button>
      </form>
      <form action={deleteProject}>
        <button className="ml-auto border py-2 px-4">Delete Project</button>
      </form>
    </div>
  );
}
