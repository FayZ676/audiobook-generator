import React from "react";
import { Suspense } from "react";

import { Script } from "../actions/script";

import ControlsClient from "./ControlsClient";

interface ControlsSectionProps {
  narrationUrlPromise: Promise<string | null>;
  scriptPromise: Promise<Script | null>;
}

export default function ControlsSection({
  narrationUrlPromise,
  scriptPromise,
}: ControlsSectionProps) {
  return (
    <Suspense fallback={<div>Loading controls ...</div>}>
      <ControlsClient
        narrationUrlPromise={narrationUrlPromise}
        scriptPromise={scriptPromise}
      />
    </Suspense>
  );
}
