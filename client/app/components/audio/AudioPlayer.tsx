"use client";

import React, { useEffect, useRef, useState } from "react";
import { CirclePlay, Pause } from "lucide-react";

interface AudioPlayerProps {
  src: string;
}

export default function AudioPlayer({ src }: AudioPlayerProps) {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setIsPlaying(false);
    setError(null);
    const el = audioRef.current;
    if (el) {
      el.load();

      const handleCanPlay = () => {
        el.play().catch(() => setError("Failed to play audio"));
        el.removeEventListener("canplay", handleCanPlay);
      };
      el.addEventListener("canplay", handleCanPlay);

      return () => {
        el.removeEventListener("canplay", handleCanPlay);
      };
    }
  }, [src]);

  const togglePlay = () => {
    const el = audioRef.current;
    if (!el) return;
    if (isPlaying) {
      el.pause();
    } else {
      el.play().catch(() => setError("Failed to play audio"));
    }
  };

  return (
    <div className="flex items-center gap-2">
      <button
        onClick={togglePlay}
        className={`btn btn-sm btn-outline ${
          isPlaying ? "btn-warning" : "btn-success"
        }`}
        title={isPlaying ? "Pause" : "Play"}
      >
        {isPlaying ? <Pause size={16} /> : <CirclePlay size={16} />}
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
