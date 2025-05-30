import React from "react";
import { Suspense } from "react";

import { getNarration } from "../actions/narrate";
import NarrationSection from "./NarrationSection";

export default function NarrationView() {
  const narrationPromise = getNarration();
  return (
    <Suspense>
      <NarrationSection narrationUrlPromise={narrationPromise} />
    </Suspense>
  );
}
