import React from "react";
import { Suspense } from "react";

import { getVoices } from "../actions/voices";
import VoicesDashboardClient from "./VoicesDashboardClient";
import AddVoiceForm from "./AddVoiceForm";

export default function VoicesDashboard() {
  const voicesPromise = getVoices();

  return (
    <div className="flex flex-col gap-6">
      <AddVoiceForm />
      <Suspense fallback={<div>Loading voices ...</div>}>
        <VoicesDashboardClient voicesPromise={voicesPromise} />
      </Suspense>
    </div>
  );
}
