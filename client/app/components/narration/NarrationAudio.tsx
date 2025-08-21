import React from "react";
import AudioPlayerLarge from "../audio/AudioPlayerLarge";

interface NarrationAudioProps {
  url: () => Promise<string>;
  disabled?: boolean;
}

export default function NarrationAudio({
  url,
  disabled = false,
}: NarrationAudioProps) {
  return (
    <div className="relative">
      <AudioPlayerLarge url={url} disabled={disabled} />
    </div>
  );
}
