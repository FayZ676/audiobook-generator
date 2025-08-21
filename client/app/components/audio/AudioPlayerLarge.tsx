"use client";

import React from "react";
import { Play, Pause, Download, LoaderCircle } from "lucide-react";
import { useLazyAudio } from "@/app/hooks/useLazyAudio";

interface AudioPlayerLargeProps {
  url: () => Promise<string>;
  disabled?: boolean;
}

export default function AudioPlayerLarge({
  url,
  disabled = false,
}: AudioPlayerLargeProps) {
  const {
    audioRef,
    loaded,
    isPlaying,
    isLoading,
    error,
    currentTime,
    duration,
    progress,
    handlePlay,
    handleDownload,
    formatTime,
    handleSliderChange,
    handleSliderMouseDown,
    handleSliderMouseUp,
    audioEventHandlers,
  } = useLazyAudio(url, { trackTime: true });

  return (
    <div className="bg-base-100 border border-base-300 rounded-md w-full px-4">
      <div className="flex items-center gap-3">
        {/* Play/Pause Button */}
        <button
          onClick={handlePlay}
          disabled={isLoading || disabled}
          className={`btn btn-circle btn-lg ${isPlaying ? "btn-warning" : ""} ${
            disabled ? "btn-disabled" : ""
          }`}
          title={
            disabled
              ? "Audio playback disabled"
              : isLoading
              ? "Loading..."
              : isPlaying
              ? "Pause"
              : "Play"
          }
        >
          {isLoading ? (
            <LoaderCircle size={20} className="animate-spin" />
          ) : isPlaying ? (
            <Pause size={20} fill="currentColor" />
          ) : (
            <Play size={20} fill="currentColor" className="ml-0.5" />
          )}
        </button>

        {/* Current Time */}
        <span className="text-sm font-mono text-gray-500">
          {formatTime(currentTime)}
        </span>

        {/* Progress Slider */}
        <div className="flex-1 relative">
          <input
            type="range"
            min="0"
            max={duration}
            value={currentTime}
            onChange={handleSliderChange}
            onMouseDown={handleSliderMouseDown}
            onMouseUp={handleSliderMouseUp}
            onTouchStart={handleSliderMouseDown}
            onTouchEnd={handleSliderMouseUp}
            disabled={disabled || duration === 0}
            className="range range-xs w-full"
            style={{
              background: `linear-gradient(to right, hsl(var(--p)) 0%, hsl(var(--p)) ${progress}%, hsl(var(--b3)) ${progress}%, hsl(var(--b3)) 100%)`,
            }}
          />
        </div>

        {/* Duration */}
        <span className="text-sm font-mono text-gray-500">
          {formatTime(duration)}
        </span>

        {/* Download Button */}
        <button
          onClick={handleDownload}
          disabled={disabled || !loaded}
          className={`btn btn-circle btn-ghost btn-sm ${
            disabled || !loaded ? "btn-disabled" : ""
          }`}
          title="Download audio file"
        >
          <Download size={20} />
        </button>
      </div>

      {error && (
        <div className="mt-2">
          <span className="text-error text-sm">{error}</span>
        </div>
      )}

      <audio
        ref={audioRef}
        preload="none"
        {...audioEventHandlers}
        className="hidden"
      />
    </div>
  );
}
