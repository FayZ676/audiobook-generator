import React from "react";
import { Suspense } from "react";

import { getVoices } from "../actions/voices";

import VoiceAddForm from "./VoiceAddForm";
import VoiceList from "./VoiceList";

export default function VoicesDashboard() {
  const voicesPromise = getVoices();

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="text-md font-semibold mb-4">Voice presets</h2>
        <Suspense fallback={<div>Loading voices ...</div>}>
          <VoiceList voicesPromise={voicesPromise} />
        </Suspense>
      </div>
      <div>
        <h2 className="text-md font-semibold mb-4">Add a new voice</h2>
        <VoiceAddForm />
      </div>
    </div>
  );
}
