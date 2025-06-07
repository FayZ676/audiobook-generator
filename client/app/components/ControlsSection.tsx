import React from "react";
import { Suspense } from "react";

import { Script } from "../actions/script";
import { AudiobookJob } from "../actions/job";

import ControlsClient from "./ControlsClient";

interface ControlsSectionProps {
  narrationUrlPromise: Promise<string | null>;
  scriptPromise: Promise<Script | null>;
  jobStatePromise: Promise<AudiobookJob | null>;
}

export default function ControlsSection({
  narrationUrlPromise,
  scriptPromise,
  jobStatePromise,
}: ControlsSectionProps) {
  return (
    <Suspense fallback={<div>Loading controls ...</div>}>
      <ControlsClient
        narrationUrlPromise={narrationUrlPromise}
        scriptPromise={scriptPromise}
        jobStatePromise={jobStatePromise}
      />
    </Suspense>
  );
}
