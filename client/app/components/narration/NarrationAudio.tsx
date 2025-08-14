import React from "react";

interface NarrationAudioProps {
  narrationUrl: string;
}

export default function NarrationAudio({ narrationUrl }: NarrationAudioProps) {
  return (
    <audio key={narrationUrl} controls className="w-full">
      <source src={narrationUrl} />
      Your browser does not support the audio element.
    </audio>
  );
}
