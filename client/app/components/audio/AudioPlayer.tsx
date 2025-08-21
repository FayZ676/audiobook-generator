"use client";

import React from "react";
import { CirclePlay, Pause, LoaderCircle } from "lucide-react";
import { useLazyAudio } from "@/app/hooks/useLazyAudio";

interface AudioPlayerProps {
  url: () => Promise<string>;
  disabled?: boolean;
}

export default function AudioPlayer({
  url,
  disabled = false,
}: AudioPlayerProps) {
  const {
    audioRef,
    isPlaying,
    isLoading,
    error,
    handlePlay,
    audioEventHandlers,
  } = useLazyAudio(url);
  return (
    <div className="flex items-center gap-2">
      <button
        onClick={handlePlay}
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
      <audio
        ref={audioRef}
        preload="none"
        {...audioEventHandlers}
        className="hidden"
      />
    </div>
  );
}
