import React from "react";
import { use } from "react";

import { Voice } from "../actions/voices";

interface VoicesDashboardClientProps {
  voicesPromise: Promise<Voice[]>;
}

export default function VoicesDashboardClient({
  voicesPromise,
}: VoicesDashboardClientProps) {
  const voices = use(voicesPromise);
  return (
    <div>
      <ul>
        {voices.map((voice) => (
          <li key={voice.name}>
            <strong>{voice.name}</strong>
          </li>
        ))}
      </ul>
    </div>
  );
}
