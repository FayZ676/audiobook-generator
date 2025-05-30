import React from "react";
import { use } from "react";

import NarrationAudio from "./NarrationAudio";
import NarrationButton from "./NarrationButton";

interface NarrationSectionProps {
  narrationUrlPromise: Promise<string | null>;
}

export default function NarrationSection({
  narrationUrlPromise,
}: NarrationSectionProps) {
  const narrationUrl = use(narrationUrlPromise);
  return (
    <>
      {narrationUrl ? (
        <NarrationAudio narrationUrl={narrationUrl} />
      ) : (
        <NarrationButton />
      )}
    </>
  );
}
