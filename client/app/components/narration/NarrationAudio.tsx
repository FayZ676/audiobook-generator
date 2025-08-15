import React from "react";

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
      <audio
        key={narrationUrl}
        controls={!disabled}
        className={`w-full ${disabled ? "opacity-50 pointer-events-none" : ""}`}
      >
        <source src={narrationUrl} />
        Your browser does not support the audio element.
      </audio>
    </div>
  );
}
