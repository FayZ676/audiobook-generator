import React from "react";

import { Voice } from "../actions/voices";

interface VoiceCardProps {
  voice: Voice;
}

export default function VoiceCard({ voice }: VoiceCardProps) {
  return (
    <div className="border p-3 rounded">
      <div className="flex justify-between items-center">
        <span className="font-medium">{voice.name}</span>
        <div className="flex gap-4 text-sm text-gray-600">
          <span>{voice.gender}</span>
          <span>{voice.age}</span>
        </div>
      </div>
    </div>
  );
}
