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
      {disabled && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-100 bg-opacity-75 rounded">
          <span className="text-sm text-gray-600">
            Audio disabled during regeneration
          </span>
        </div>
      )}
    </div>
  );
}
