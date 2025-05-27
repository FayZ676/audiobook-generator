"use client";

import React, { useState } from "react";
import useSWR from "swr";

import { NarrationUrl } from "../actions/narrate";

// SWR fetcher function
const fetcher = async (url: string) => {
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error('An error occurred while fetching the data.');
  }
  return res.json();
};

interface NarrationViewProps {
  // No props needed anymore as we fetch directly in the component
}

export default function NarrationView({}: NarrationViewProps) {
  const [shouldFetch, setShouldFetch] = useState(false);
  
  // Only fetch when the user clicks the button
  const { data: narrationUrl, error, isLoading } = useSWR(
    shouldFetch ? '/api/narration' : null,
    fetcher
  );

  const loadAudio = () => {
    setShouldFetch(true);
  };

  return (
    <div className="w-full">
      {!shouldFetch && (
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
          Failed to load audio. Please try again.
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
