"use client";

import React, { useEffect, useRef, useState } from "react";
import { CirclePlay, Pause, LoaderCircle } from "lucide-react";

interface AudioPlayerProps {
  src?: string | null;
  autoPlay?: boolean;
  loadSrc?: () => Promise<string | null>;
}

export default function AudioPlayer({
  src = null,
  autoPlay = false,
  loadSrc,
}: AudioPlayerProps) {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [internalSrc, setInternalSrc] = useState<string | null>(src);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setInternalSrc(src ?? null);
    setIsPlaying(false);
    setError(null);
  }, [src]);

  useEffect(() => {
    if (autoPlay && internalSrc && audioRef.current) {
      audioRef.current
        .play()
        .then(() => setIsPlaying(true))
        .catch(() => setError("Unable to autoplay"));
    }
  }, [autoPlay, internalSrc]);

  const togglePlay = () => {
    const el = audioRef.current;
    if (!el) return;
    if (isPlaying) {
      el.pause();
    } else {
      el.play().catch(() => setError("Failed to play audio"));
    }
  };

  const load = async () => {
    if (internalSrc || isLoading || !loadSrc) return;
    setIsLoading(true);
    setError(null);
    try {
      const url = await loadSrc();
      setInternalSrc(url ?? null);
    } catch {
      setError("Failed to load audio");
    } finally {
      setIsLoading(false);
    }
  };

  if (!internalSrc && loadSrc) {
    return (
      <div className="flex items-center gap-2">
        <button
          onClick={load}
          disabled={isLoading}
          className="btn btn-success btn-outline btn-sm"
          title="Play sample"
        >
          {isLoading ? (
            <LoaderCircle size={16} className="animate-spin" />
          ) : (
            <CirclePlay size={16} />
          )}
        </button>
        {error && <span className="text-red-500 text-xs">{error}</span>}
      </div>
    );
  }

  if (!internalSrc) {
    return null;
  }

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
        <source src={internalSrc} />
      </audio>
    </div>
  );
}
