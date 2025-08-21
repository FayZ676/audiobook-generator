import React from "react";

import { getVoices } from "../../actions/voices";

import VoicesDashboardClient from "@/app/components/voices/VoicesDashboardClient";

export default async function VoicesDashboard() {
  const voicesPromise = getVoices();

  return <VoicesDashboardClient voicesPromise={voicesPromise} />;
}
