import React from "react";
import { Suspense } from "react";

import NarrationClient from "./NarrationClient";

interface NarrationSectionProps {
  narrationUrlPromise: Promise<string | null>;
}

export default function NarrationSection({
  narrationUrlPromise,
}: NarrationSectionProps) {
  return (
    <Suspense fallback={<div>Loading narration ...</div>}>
      <NarrationClient narrationUrlPromise={narrationUrlPromise} />
    </Suspense>
  );
}
