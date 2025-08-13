"use client";

import React, { useEffect, useRef, useState } from "react";
import { CirclePlay, Pause, LoaderCircle } from "lucide-react";

interface AudioPlayerProps {
  src: string;
}

export default function AudioPlayer({ src }: AudioPlayerProps) {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setIsPlaying(false);
    setIsLoading(false);
    setError(null);
    const el = audioRef.current;
    if (el) {
      el.load();
    }
  }, [src]);

  const togglePlay = async () => {
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
        disabled={isLoading}
        className={`btn btn-sm btn-outline ${
          isPlaying ? "btn-warning" : "btn-success"
        } ${isLoading ? "loading" : ""}`}
        title={isLoading ? "Loading..." : isPlaying ? "Pause" : "Play"}
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
