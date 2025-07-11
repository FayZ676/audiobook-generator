import React, { Suspense } from "react";

import { Voice } from "../../actions/voices";
import { AudiobookJob } from "../../actions/job";

import ScriptManagerClient from "./ScriptManagerClient";

interface ScriptInfo {
  filename: string;
  s3_key: string;
}

interface ScriptManagerProps {
  scriptsPromise: Promise<ScriptInfo[]>;
  voicesPromise: Promise<Voice[]>;
  narrationUrlPromise: Promise<string | null>;
  jobStatePromise: Promise<AudiobookJob | null>;
}

export default function ScriptManager({
  scriptsPromise,
  voicesPromise,
  narrationUrlPromise,
  jobStatePromise,
}: ScriptManagerProps) {
  return (
    <Suspense
      fallback={
        <div>
          Loading scripts{" "}
          <span className="loading loading-dots loading-xs"></span>
        </div>
      }
    >
      <ScriptManagerClient
        scriptsPromise={scriptsPromise}
        voicesPromise={voicesPromise}
        narrationUrlPromise={narrationUrlPromise}
        jobStatePromise={jobStatePromise}
      />
    </Suspense>
  );
}
