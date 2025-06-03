import React from "react";
import { Suspense } from "react";

import { Voice } from "@/app/actions/voices";

interface VoicesSectionProps {
  voicesPromise: Promise<Voice[]>;
}

export default function VoicesSection(voicesSectionProps: VoicesSectionProps) {
  return (
    <Suspense fallback={<div>Loading voices ...</div>}>
      <div>VoicesSection</div>;
    </Suspense>
  );
}
