import React from "react";
import { Suspense } from "react";

import { getNarration } from "../actions/narrate";
import NarrationClient from "./NarrationClient";

export default function NarrationSection() {
  const narrationPromise = getNarration();
  return (
    <Suspense fallback={<div>Loading narration ...</div>}>
      <NarrationClient narrationUrlPromise={narrationPromise} />
    </Suspense>
  );
}
