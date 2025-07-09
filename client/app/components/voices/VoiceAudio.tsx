"use client";

import React, { useState } from "react";
import { CirclePlay, LoaderCircle } from "lucide-react";

import { getVoiceAudioUrl } from "../../actions/voices";

interface VoiceAudioProps {
  voiceName: string;
}

export default function VoiceAudio({ voiceName }: VoiceAudioProps) {
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
          className="p-1 rounded-full transition-transform duration-200 hover:-translate-y-0.5"
        >
          <CirclePlay size={20} />
        </button>
      )}

      {loading && (
        <div className="p-1">
          <LoaderCircle size={20} className="animate-spin" />
        </div>
      )}

      {error && <span className="text-sm text-red-500">{error}</span>}

      {audioUrl && !loading && (
        <>
          <button
            onClick={handlePlayPause}
            className={`p-1 rounded-full transition-transform duration-200 hover:-translate-y-0.5 ${
              isPlaying ? "animate-spin" : ""
            }`}
          >
            <CirclePlay size={20} />
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
