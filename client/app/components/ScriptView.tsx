import React from "react";
import { Suspense } from "react";

import { getScript } from "@/app/actions/script";

import ScriptClient from "@/app/components/ScriptClient";

export default async function ScriptView() {
  const script = getScript();
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <ScriptClient scriptPromise={script} />
    </Suspense>
  );
}
