import React from "react";
import { Suspense } from "react";

import { Script } from "../actions/script";
import ScriptClient from "@/app/components/ScriptClient";

interface ScriptSectionProps {
  scriptPromise: Promise<Script | null>;
}

export default async function ScriptSection({
  scriptPromise,
}: ScriptSectionProps) {
  return (
    <Suspense fallback={<div>Loading script ...</div>}>
      <ScriptClient scriptPromise={scriptPromise} />
    </Suspense>
  );
}
