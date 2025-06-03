import React from "react";
import { use } from "react";

import { Voice } from "../actions/voices";

import VoiceCard from "./VoiceCard";

interface VoicesDashboardClientProps {
  voicesPromise: Promise<Voice[]>;
}

export default function VoicesDashboardClient({
  voicesPromise,
}: VoicesDashboardClientProps) {
  const voices = use(voicesPromise);
  return (
    <div>
      <ul className="grid grid-cols-2 gap-2">
        {voices.map((voice) => (
          <li key={voice.name}>
            <VoiceCard voice={voice} />
          </li>
        ))}
      </ul>
    </div>
  );
}
