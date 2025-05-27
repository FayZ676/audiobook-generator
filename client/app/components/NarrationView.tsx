"use client";

import React, { useState } from "react";

import { NarrationUrl } from "../actions/narrate";

interface NarrationViewProps {
  getNarrationUrl: () => Promise<NarrationUrl | null>;
}

export default function NarrationView({ getNarrationUrl }: NarrationViewProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [narrationUrl, setNarrationUrl] = useState<NarrationUrl | null>(null);
  const [error, setError] = useState<string | null>(null);

  const loadAudio = async () => {
    if (narrationUrl) return; // Already loaded
    
    setIsLoading(true);
    setError(null);
    
    try {
      const url = await getNarrationUrl();
      setNarrationUrl(url);
    } catch (err) {
      setError("Failed to load audio. Please try again.");
      console.error("Error loading narration:", err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full">
      {!narrationUrl && !isLoading && (
        <button
          onClick={loadAudio}
          className="w-full border py-2 px-4 bg-gray-100 hover:bg-gray-200"
        >
          Load Audio
        </button>
      )}
      
      {isLoading && (
        <div className="text-center py-4">
          Loading audio...
        </div>
      )}
      
      {error && (
        <div className="text-red-500 text-center py-2">
          {error}
        </div>
      )}
      
      {narrationUrl && (
        <audio controls preload="none">
          <source src={narrationUrl} />
          Your browser does not support the audio element.
        </audio>
      )}
    </div>
  );
}
