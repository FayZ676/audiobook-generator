import React from "react";
import { Suspense } from "react";

import { getVoices } from "../actions/voices";

import VoiceAddForm from "./VoiceAddForm";
import VoiceList from "./VoiceList";

export default function VoicesDashboard() {
  const voicesPromise = getVoices();

  return (
    <div className="flex flex-col gap-6">
      <Suspense fallback={<div>Loading voices ...</div>}>
        <VoiceList voicesPromise={voicesPromise} />
      </Suspense>
      <VoiceAddForm />
    </div>
  );
}
