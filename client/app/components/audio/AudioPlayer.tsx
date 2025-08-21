"use client";

import React from "react";
import { CirclePlay, Pause, LoaderCircle } from "lucide-react";
import { useAudioPlayer } from "@/app/hooks/useAudioPlayer";

interface AudioPlayerProps {
  src: string;
  disabled?: boolean;
}

export default function AudioPlayer({
  src,
  disabled = false,
}: AudioPlayerProps) {
  const {
    audioRef,
    isPlaying,
    isLoading,
    error,
    togglePlay,
    audioEventHandlers,
  } = useAudioPlayer(src, { disabled });

  return (
    <div className="flex items-center gap-2">
      <button
        onClick={togglePlay}
        disabled={isLoading || disabled}
        className={`btn btn-sm btn-outline ${
          isPlaying ? "btn-warning" : "btn-success"
        } ${isLoading ? "loading" : ""} ${disabled ? "btn-disabled" : ""}`}
        title={
          disabled
            ? "Audio playback disabled during regeneration"
            : isLoading
            ? "Loading..."
            : isPlaying
            ? "Pause"
            : "Play"
        }
      >
        {isLoading ? (
          <LoaderCircle size={16} className="animate-spin" />
        ) : isPlaying ? (
          <Pause size={16} />
        ) : (
          <CirclePlay size={16} />
        )}
      </button>
      {error && <span className="text-red-500 text-xs">{error}</span>}
      <audio ref={audioRef} {...audioEventHandlers} className="hidden">
        <source src={src} />
      </audio>
    </div>
  );
}
