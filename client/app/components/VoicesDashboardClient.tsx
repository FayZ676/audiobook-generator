import React from "react";

import { Voice } from "../actions/voices";

interface VoicesDashboardClientProps {
  voicesPromise: Promise<Voice[]>;
}

export default function VoicesDashboardClient({
  voicesPromise,
}: VoicesDashboardClientProps) {
  return <div>VoicesDashboardClient</div>;
}
