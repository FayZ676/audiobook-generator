import React from "react";
import { Suspense } from "react";

import { getVoices } from "../actions/voices";
import VoiceList from "./VoiceList";

export default function VoicesDashboard() {
  const voicesPromise = getVoices();

  return (
    <Suspense fallback={<div>Loading voices ...</div>}>
      <VoiceList voicesPromise={voicesPromise} />
    </Suspense>
  );
}
