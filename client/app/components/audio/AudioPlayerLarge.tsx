"use client";

import React from "react";
import { Play, Pause, Download, LoaderCircle } from "lucide-react";
import { useAudioPlayer } from "@/app/hooks/useAudioPlayer";

interface AudioPlayerLargeProps {
  src: string;
  disabled?: boolean;
}

export default function AudioPlayerLarge({
  src,
  disabled = false,
}: AudioPlayerLargeProps) {
  const {
    audioRef,
    isPlaying,
    isLoading,
    error,
    currentTime,
    duration,
    setIsDragging,
    togglePlay,
    seekTo,
    audioEventHandlers,
  } = useAudioPlayer(src, { disabled, trackTime: true });

  const formatTime = (seconds: number): string => {
    if (!isFinite(seconds) || isNaN(seconds)) return "0:00";
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  const handleSliderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newTime = parseFloat(e.target.value);
    seekTo(newTime);
  };

  const handleSliderMouseDown = () => {
    setIsDragging(true);
  };

  const handleSliderMouseUp = () => {
    setIsDragging(false);
  };

  const handleDownload = () => {
    if (!src) return;

    const link = document.createElement("a");
    link.href = src;
    link.download = `narration-${Date.now()}.mp3`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const progress = duration > 0 ? (currentTime / duration) * 100 : 0;

  return (
    <div className="bg-base-100 border border-base-300 rounded-md w-full px-4">
      <div className="flex items-center gap-3">
        {/* Play/Pause Button */}
        <button
          onClick={togglePlay}
          disabled={isLoading || disabled}
          className={`btn btn-circle btn-lg ${isPlaying ? "btn-warning" : ""} ${
            disabled ? "btn-disabled" : ""
          }`}
          title="Play Button"
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
            className="range range-sm w-full"
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
          disabled={disabled || !src}
          className={`btn btn-circle btn-ghost btn-sm ${
            disabled ? "btn-disabled" : ""
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

      <audio ref={audioRef} {...audioEventHandlers} className="hidden">
        <source src={src} />
      </audio>
    </div>
  );
}
