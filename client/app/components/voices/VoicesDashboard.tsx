import React from "react";

import { getVoices, getVoiceAudioUrls } from "../../actions/voices";

import VoicesDashboardClient from "@/app/components/voices/VoicesDashboardClient";

export default async function VoicesDashboard() {
  const voicesPromise = getVoices();
  const voices = await voicesPromise;
  const voiceAudioUrls = await getVoiceAudioUrls(voices);

  const voiceAudioData = {
    urls: voiceAudioUrls,
  };

  return (
    <VoicesDashboardClient
      voicesPromise={Promise.resolve(voices)}
      voiceAudioData={voiceAudioData}
    />
  );
}
