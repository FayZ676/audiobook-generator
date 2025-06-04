import React from "react";
import { use } from "react";

import { Voice } from "../actions/voices";

import VoiceCard from "./VoiceCard";

interface VoiceListProps {
  voicesPromise: Promise<Voice[]>;
}

export default function VoiceList({
  voicesPromise,
}: VoiceListProps) {
  const voices = use(voicesPromise);
  return (
    <div className="h-64 overflow-y-auto">
      <ul className="grid grid-cols-1 gap-2">
        {voices.map((voice) => (
          <li key={voice.name}>
            <VoiceCard voice={voice} />
          </li>
        ))}
      </ul>
    </div>
  );
}
