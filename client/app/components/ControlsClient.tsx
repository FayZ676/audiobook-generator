"use client";

import React from "react";
import { use } from "react";

import { createNarration } from "../actions/narrate";
import { deleteProject } from "../actions/audiobook";
import { Script } from "../actions/script";

interface ControlsClientProps {
  narrationUrlPromise: Promise<string | null>;
  scriptPromise: Promise<Script | null>;
}

export default function ControlsClient({
  narrationUrlPromise,
  scriptPromise,
}: ControlsClientProps) {
  const narrationUrl = use(narrationUrlPromise);
  const script = use(scriptPromise);

  return (
    <div className="flex gap-4">
      {script && !narrationUrl && (
        <button
          onClick={(e) => {
            e.preventDefault();
            createNarration();
          }}
          className="ml-auto border py-2 px-4"
        >
          Narrate
        </button>
      )}
      {(script || narrationUrl) && (
        <button
          onClick={(e) => {
            e.preventDefault();
            deleteProject();
          }}
          className="ml-auto border py-2 px-4"
        >
          Delete Project
        </button>
      )}
    </div>
  );
}
