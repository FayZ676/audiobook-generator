import React from "react";

interface NarrationAudioProps {
  narrationUrl: string;
}

export default function NarrationAudio({ narrationUrl }: NarrationAudioProps) {
  return (
    <audio controls>
      <source src={narrationUrl} />
      Your browser does not support the audio element.
    </audio>
  );
}
