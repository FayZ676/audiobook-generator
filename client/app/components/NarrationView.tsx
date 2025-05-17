import React from "react";

import { Script } from "../actions/script";
import { NarrationUrl } from "../actions/narrate";

interface NarrationViewProps {
  script: Script;
  narrationUrl: NarrationUrl | null;
  createNarration: (script: Script) => Promise<void>;
}

export default function NarrationView({
  script,
  narrationUrl,
  createNarration,
}: NarrationViewProps) {
  return (
    <>
      {narrationUrl ? (
        <audio controls>
          <source src={narrationUrl} />
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
