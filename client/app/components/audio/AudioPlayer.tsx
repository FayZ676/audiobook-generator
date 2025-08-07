"use client";

import React, { useState } from "react";
import { CirclePlay, LoaderCircle, Pause } from "lucide-react";

import { getVoiceAudioUrl } from "../../actions/voices";

interface AudioPlayerProps {
  voiceName: string;
}

export default function AudioPlayer({ voiceName }: AudioPlayerProps) {
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);

  const loadAudioUrl = async () => {
    if (audioUrl || loading) return;

    setLoading(true);
    setError(null);

    try {
      const url = await getVoiceAudioUrl(voiceName);
      setAudioUrl(url);
      if (!url) {
        setError("Audio not available");
      } else {
        setTimeout(() => {
          const audio = document.getElementById(
            `audio-${voiceName}`
          ) as HTMLAudioElement;
          if (audio) {
            audio.play();
          }
        }, 100);
      }
    } catch (err) {
      setError("Failed to load audio");
      console.error("Error loading voice audio:", err);
    } finally {
      setLoading(false);
    }
  };

  const handlePlayPause = () => {
    const audio = document.getElementById(
      `audio-${voiceName}`
    ) as HTMLAudioElement;
    if (audio) {
      if (isPlaying) {
        audio.pause();
      } else {
        audio.play();
      }
    }
  };

  return (
    <div className="flex items-center gap-2">
      {!audioUrl && !loading && (
        <button
          onClick={loadAudioUrl}
          className="btn btn-success btn-outline btn-sm"
        >
          <CirclePlay size={14} />
        </button>
      )}

      {loading && (
        <button className="btn btn-disabled btn-outline btn-sm">
          <LoaderCircle size={14} className="animate-spin" />
        </button>
      )}

      {error && <span className="text-sm text-red-500">{error}</span>}

      {audioUrl && !loading && (
        <>
          <button
            onClick={handlePlayPause}
            className={`btn btn-sm btn-outline ${
              isPlaying ? "btn-warning" : "btn-success"
            }`}
          >
            {isPlaying ? <Pause size={14} /> : <CirclePlay size={14} />}
          </button>
          <audio
            id={`audio-${voiceName}`}
            onPlay={() => setIsPlaying(true)}
            onPause={() => setIsPlaying(false)}
            onEnded={() => setIsPlaying(false)}
            className="hidden"
          >
            <source src={audioUrl} />
          </audio>
        </>
      )}
    </div>
  );
}
