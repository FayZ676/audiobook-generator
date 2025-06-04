import React from "react";
import { Suspense } from "react";

import { getVoices } from "../actions/voices";
import VoicesDashboardClient from "./VoicesDashboardClient";
import VoiceAddForm from "./VoiceAddForm";

export default function VoicesDashboard() {
  const voicesPromise = getVoices();

  return (
    <div className="flex flex-col gap-6">
      <VoiceAddForm />
      <Suspense fallback={<div>Loading voices ...</div>}>
        <VoicesDashboardClient voicesPromise={voicesPromise} />
      </Suspense>
    </div>
  );
}
