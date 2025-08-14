"use client";

import React, { useEffect, useRef, useState } from "react";
import { CirclePlay, Pause, LoaderCircle } from "lucide-react";

interface AudioPlayerProps {
  src: string;
  disabled?: boolean;
  onPlayStateChange?: (isPlaying: boolean) => void;
}

export default function AudioPlayer({
  src,
  disabled = false,
  onPlayStateChange,
}: AudioPlayerProps) {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const el = audioRef.current;
    if (!el) return;

    setIsPlaying(false);
    setIsLoading(false);
    setError(null);
    el.load();
  }, [src]);

  useEffect(() => {
    const el = audioRef.current;
    if (disabled && isPlaying && el) {
      el.pause();
    }
  }, [disabled]);

  const togglePlay = async () => {
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
      <audio
        ref={audioRef}
        onPlay={() => {
          setIsPlaying(true);
          onPlayStateChange?.(true);
        }}
        onPause={() => {
          setIsPlaying(false);
          onPlayStateChange?.(false);
        }}
        onEnded={() => {
          setIsPlaying(false);
          onPlayStateChange?.(false);
        }}
        onError={() => setError("Audio error")}
        className="hidden"
      >
        <source src={src} />
      </audio>
    </div>
  );
}
