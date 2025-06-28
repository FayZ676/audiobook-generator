"use client";

import React, { useState } from "react";

import { getVoiceAudioUrl } from "../../actions/voices";

interface VoiceAudioProps {
  voiceName: string;
}

export default function VoiceAudio({ voiceName }: VoiceAudioProps) {
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadAudioUrl = async () => {
    if (audioUrl || loading) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const url = await getVoiceAudioUrl(voiceName);
      setAudioUrl(url);
      if (!url) {
        setError("Audio not available");
      }
    } catch (err) {
      setError("Failed to load audio");
      console.error("Error loading voice audio:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center gap-2">
      {!audioUrl && !loading && !error && (
        <button
          onClick={loadAudioUrl}
          className="text-blue-600 hover:text-blue-800 text-sm underline"
        >
          Play Sample
        </button>
      )}
      
      {loading && (
        <span className="text-sm text-gray-500">Loading...</span>
      )}
      
      {error && (
        <span className="text-sm text-red-500">{error}</span>
      )}
      
      {audioUrl && (
        <audio controls className="h-8">
          <source src={audioUrl} />
          Your browser does not support the audio element.
        </audio>
      )}
    </div>
  );
}