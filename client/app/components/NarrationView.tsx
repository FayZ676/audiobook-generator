import React from "react";
import { Suspense } from "react";

import { getNarration } from "../actions/narrate";
import NarrationClient from "./NarrationClient";

export default function NarrationView() {
  const narrationPromise = getNarration();
  return (
    <Suspense>
      <NarrationClient narrationUrlPromise={narrationPromise} />
    </Suspense>
  );
}
