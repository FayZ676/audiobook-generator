import React from "react";
import { Suspense } from "react";

import { getScript } from "@/app/actions/script";

import ScriptText from "@/app/components/ScriptText";

export default async function ScriptView() {
  const script = getScript();
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <ScriptText scriptPromise={script} />
    </Suspense>
  );
}
