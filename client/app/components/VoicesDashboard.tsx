import React from "react";
import { Suspense } from "react";

import { getVoices } from "../actions/voices";
import VoicesDashboardClient from "./VoicesDashboardClient";

export default function VoicesDashboard() {
  const voicesPromise = getVoices();

  return (
    <Suspense fallback={<div>Loading voices ...</div>}>
      <VoicesDashboardClient voicesPromise={voicesPromise} />
    </Suspense>
  );
}
