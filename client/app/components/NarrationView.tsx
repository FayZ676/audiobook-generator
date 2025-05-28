"use client";

import React, { useState, useEffect } from "react";
import { getNarrationClient } from "../actions/getNarrationClient";

interface NarrationViewProps {
  userId: string;
}

export default function NarrationView({ userId }: NarrationViewProps) {
  const [narrationUrl, setNarrationUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchNarration = async () => {
      try {
        setIsLoading(true);
        const url = await getNarrationClient(userId);
        setNarrationUrl(url);
      } catch (err) {
        setError("Failed to load audio");
        console.error("Error fetching narration:", err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchNarration();
  }, [userId]);

  if (isLoading) {
    return <div className="text-center py-4">Loading audio...</div>;
  }

  if (error || !narrationUrl) {
    return <div className="text-center py-4 text-red-500">{error || "Audio not available"}</div>;
  }

  return (
    <audio controls>
      <source src={narrationUrl} />
      Your browser does not support the audio element.
    </audio>
  );
}
