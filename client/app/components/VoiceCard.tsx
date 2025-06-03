import React from "react";

import { Voice } from "../actions/voices";

interface VoiceCardProps {
  voice: Voice;
}

export default function VoiceCard({ voice }: VoiceCardProps) {
  return (
    <div className="border p-2">
      <h3>{voice.name}</h3>
      <p>{voice.gender}</p>
      <p>{voice.age}</p>
    </div>
  );
}
