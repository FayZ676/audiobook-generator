import React, { Suspense } from "react";

import { Script } from "../actions/script";
import { Voice } from "../actions/voices";
import ScriptClient from "@/app/components/ScriptClient";

interface ScriptSectionProps {
  scriptPromise: Promise<Script | null>;
  voicesPromise: Promise<Voice[]>;
}

export default async function ScriptSection({
  scriptPromise,
  voicesPromise,
}: ScriptSectionProps) {
  return (
    <Suspense
      fallback={
        <div>
          Loading script{" "}
          <span className="loading loading-dots loading-xs"></span>
        </div>
      }
    >
      <ScriptClient
        scriptPromise={scriptPromise}
        voicesPromise={voicesPromise}
      />
    </Suspense>
  );
}
