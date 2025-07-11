import React from "react";

import { getVoices } from "../../actions/voices";

import VoicesDashboardClient from "@/app/components/voices/VoicesDashboardClient";

export default function VoicesDashboard() {
  const voicesPromise = getVoices();

  return <VoicesDashboardClient voicesPromise={voicesPromise} />;
}
