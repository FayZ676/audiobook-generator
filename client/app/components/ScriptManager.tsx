import React, { Suspense } from "react";

import { Script } from "../actions/script";
import { Voice } from "../actions/voices";
import { AudiobookJob } from "../actions/job";

import ScriptManagerClient from "./ScriptManagerClient";

interface ScriptManagerProps {
  scriptPromise: Promise<Script | null>;
  voicesPromise: Promise<Voice[]>;
  narrationUrlPromise: Promise<string | null>;
  jobStatePromise: Promise<AudiobookJob | null>;
}

export default function ScriptManager({
  scriptPromise,
  voicesPromise,
  narrationUrlPromise,
  jobStatePromise,
}: ScriptManagerProps) {
  return (
    <Suspense
      fallback={
        <div>
          Loading script{" "}
          <span className="loading loading-dots loading-xs"></span>
        </div>
      }
    >
      <ScriptManagerClient
        scriptPromise={scriptPromise}
        voicesPromise={voicesPromise}
        narrationUrlPromise={narrationUrlPromise}
        jobStatePromise={jobStatePromise}
      />
    </Suspense>
  );
}
