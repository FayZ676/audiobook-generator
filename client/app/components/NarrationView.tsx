import React from "react";

import { Script } from "../actions/script";
import { Narration } from "../actions/narrate";

interface NarrationViewProps {
  script: Script;
  narration: Narration | null;
  createNarration: (script: Script) => Promise<void>;
}

export default function NarrationView({
  script,
  narration,
  createNarration,
}: NarrationViewProps) {
  return (
    <>
      {narration ? (
        <audio controls>
          <source src={narration.audioUrl} type={narration.contentType} />
          Your browser does not support the audio element.
        </audio>
      ) : (
        <button
          onClick={(e) => {
            e.preventDefault();
            createNarration(script);
          }}
          className="ml-auto border px-4 py-2"
        >
          Narrate
        </button>
      )}
    </>
  );
}
