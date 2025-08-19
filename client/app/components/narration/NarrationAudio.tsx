import React from "react";
import AudioPlayerLarge from "../audio/AudioPlayerLarge";

interface NarrationAudioProps {
  narrationUrl: string;
  disabled?: boolean;
}

export default function NarrationAudio({
  narrationUrl,
  disabled = false,
}: NarrationAudioProps) {
  return (
    <div className="relative">
      <AudioPlayerLarge src={narrationUrl} disabled={disabled} />
    </div>
  );
}
