import React from "react";

import { Voice } from "../../actions/voices";
import VoiceAudio from "./VoiceAudio";

interface VoiceCardProps {
  voice: Voice;
}

export default function VoiceCard({ voice }: VoiceCardProps) {
  return (
    <div className="flex border-b border-gray-200 p-2">
      <div className="mr-4">
        <VoiceAudio voiceName={voice.name} />
      </div>
      <div className="flex w-full justify-between items-center">
        <span className="font-medium">{voice.name}</span>
        <div className="flex ml-auto gap-4 text-sm text-gray-600">
          <span>{voice.gender}</span>
          <span>{voice.age}</span>
        </div>
      </div>
    </div>
  );
}
