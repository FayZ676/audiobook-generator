"use client";

import React, { useState, useRef, useEffect } from "react";
import { Play, Pause, Download, LoaderCircle } from "lucide-react";

interface AudioPlayerLargeProps {
  src: string;
  disabled?: boolean;
}

export default function AudioPlayerLarge({
  src,
  disabled = false,
}: AudioPlayerLargeProps) {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [isDragging, setIsDragging] = useState(false);

  useEffect(() => {
    const el = audioRef.current;
    if (!el) return;

    setIsPlaying(false);
    setIsLoading(false);
    setError(null);
    setCurrentTime(0);
    setDuration(0);
    el.load();
  }, [src]);

  useEffect(() => {
    const el = audioRef.current;
    if (!el) return;

    const updateTime = () => {
      if (!isDragging) {
        setCurrentTime(el.currentTime);
      }
    };

    const updateDuration = () => {
      setDuration(el.duration || 0);
    };

    el.addEventListener("timeupdate", updateTime);
    el.addEventListener("loadedmetadata", updateDuration);
    el.addEventListener("durationchange", updateDuration);

    return () => {
      el.removeEventListener("timeupdate", updateTime);
      el.removeEventListener("loadedmetadata", updateDuration);
      el.removeEventListener("durationchange", updateDuration);
    };
  }, [isDragging]);

  const formatTime = (seconds: number): string => {
    if (!isFinite(seconds) || isNaN(seconds)) return "0:00";
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  const handlePlayPause = async () => {
    if (disabled) return;

    const el = audioRef.current;
    if (!el) return;

    if (isPlaying) {
      el.pause();
    } else {
      try {
        setIsLoading(true);
        setError(null);
        await el.play();
      } catch (err) {
        setError("Failed to play audio");
        console.error("Audio play error:", err);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleSliderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const el = audioRef.current;
    if (!el) return;

    const newTime = parseFloat(e.target.value);
    setCurrentTime(newTime);
    el.currentTime = newTime;
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
    <div className="bg-base-100 border border-base-300 rounded-lg p-4 shadow-sm max-w-2xl mx-auto">
      <div className="flex items-center gap-3">
        {/* Play/Pause Button */}
        <button
          onClick={handlePlayPause}
          disabled={isLoading || disabled}
          className={`btn btn-circle btn-lg ${
            isPlaying ? "btn-warning" : "btn-primary"
          } ${disabled ? "btn-disabled" : ""}`}
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
            <LoaderCircle size={20} className="animate-spin" />
          ) : isPlaying ? (
            <Pause size={20} fill="currentColor" />
          ) : (
            <Play size={20} fill="currentColor" className="ml-0.5" />
          )}
        </button>

        {/* Current Time */}
        <span className="text-sm font-mono text-base-content min-w-[2.5rem]">
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
            className="range range-primary w-full"
            style={{
              background: `linear-gradient(to right, hsl(var(--p)) 0%, hsl(var(--p)) ${progress}%, hsl(var(--b3)) ${progress}%, hsl(var(--b3)) 100%)`,
            }}
          />
        </div>

        {/* Duration */}
        <span className="text-sm font-mono text-base-content min-w-[2.5rem]">
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
          <Download size={16} />
        </button>
      </div>

      {error && (
        <div className="mt-2">
          <span className="text-error text-sm">{error}</span>
        </div>
      )}

      <audio
        ref={audioRef}
        onPlay={() => setIsPlaying(true)}
        onPause={() => setIsPlaying(false)}
        onEnded={() => setIsPlaying(false)}
        onError={() => setError("Audio error")}
        className="hidden"
      >
        <source src={src} />
      </audio>
    </div>
  );
}